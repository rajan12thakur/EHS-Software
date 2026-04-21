from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import *
from .models import *


def _is_auditor_or_admin(user):
    role_name = (getattr(user, "role_name", "") or "").upper()
    return user.is_superuser or role_name in {"AUDITOR", "ADMIN"} or getattr(user, "is_admin_user", False)


def _is_manager_or_admin(user):
    role_name = (getattr(user, "role_name", "") or "").upper()
    return user.is_superuser or role_name in {"ADMIN", "EHS MANAGER", "EHS_MANAGER"} or getattr(user, "is_admin_user", False)


def _build_execution_initial(schedule):
    responses_by_question = {
        response.question_id: response
        for response in schedule.responses.select_related("question")
    }
    initial = []
    for question in schedule.template.questions.all():
        response = responses_by_question.get(question.id)
        initial.append(
            {
                "response_id": response.id if response else "",
                "question_id": question.id,
                "previous_status": response.status if response else "",
                "status": response.status if response else "",
                "comment": response.comment if response else "",
                "observation_detail": (
                    schedule.findings.filter(origin_question=question, is_archived=False)
                    .values_list("observation_detail", flat=True)
                    .first()
                    or ""
                ),
                "risk_score": (
                    schedule.findings.filter(origin_question=question, is_archived=False)
                    .values_list("risk_score", flat=True)
                    .first()
                    or AuditFinding.RISK_MAJOR
                ),
            }
        )
    return initial


class AuditorOrAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not _is_auditor_or_admin(request.user):
            messages.error(request, "Only users with Auditor or Admin roles can start an audit.")
            return redirect("audits:schedule_list")
        return super().dispatch(request, *args, **kwargs)


class ManagerOrAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not _is_manager_or_admin(request.user):
            messages.error(request, "Only an EHS Manager or Admin can perform this action.")
            return redirect("audits:finding_dashboard")
        return super().dispatch(request, *args, **kwargs)


class AuditCategoryListView(LoginRequiredMixin, ListView):
    model = AuditCategory
    template_name = "audits/category_list.html"
    context_object_name = "categories"
    paginate_by = 10

    def get_queryset(self):
        queryset = AuditCategory.objects.annotate(template_count=Count("templates")).order_by("category_name")
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "").strip()

        if search:
            queryset = queryset.filter(
                Q(category_name__icontains=search)
                | Q(category_code__icontains=search)
                | Q(description__icontains=search)
            )
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "").strip()
        context["selected_status"] = self.request.GET.get("status", "").strip()
        return context


class AuditCategoryCreateView(LoginRequiredMixin, CreateView):
    model = AuditCategory
    form_class = AuditCategoryForm
    template_name = "audits/category_form.html"
    success_url = reverse_lazy("audits:category_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Audit category created successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Audit Category"
        return context


class AuditCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = AuditCategory
    form_class = AuditCategoryForm
    template_name = "audits/category_form.html"
    success_url = reverse_lazy("audits:category_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Audit category updated successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Audit Category"
        return context


class AuditCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = AuditCategory
    template_name = "audits/category_confirm_delete.html"
    success_url = reverse_lazy("audits:category_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Audit category deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template_count"] = self.object.templates.count()
        return context


class AuditTemplateListView(LoginRequiredMixin, ListView):
    model = AuditTemplate
    template_name = "audits/template_list.html"
    context_object_name = "templates"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            AuditTemplate.objects.select_related("category")
            .annotate(question_count=Count("questions"))
            .order_by("title", "version")
        )
        search = self.request.GET.get("search", "").strip()
        category_id = self.request.GET.get("category", "").strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(version__icontains=search)
                | Q(standard_reference__icontains=search)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = AuditCategory.objects.filter(is_active=True).order_by("category_name")
        context["search"] = self.request.GET.get("search", "").strip()
        context["selected_category"] = self.request.GET.get("category", "").strip()
        return context


class AuditTemplateCreateView(LoginRequiredMixin, CreateView):
    model = AuditTemplate
    form_class = AuditTemplateForm
    template_name = "audits/template_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Audit template created successfully.")
        return response

    def get_success_url(self):
        return reverse("audits:template_detail", kwargs={"pk": self.object.pk})


class AuditTemplateDetailView(LoginRequiredMixin, DetailView):
    model = AuditTemplate
    template_name = "audits/template_detail.html"
    context_object_name = "template"

    def get_queryset(self):
        return AuditTemplate.objects.select_related("category").prefetch_related("questions", "schedules")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = self.object.questions.all().order_by("sequence", "id")
        context["questions"] = questions
        context["question_count"] = questions.count()
        context["schedule_count"] = self.object.schedules.count()
        return context


class AuditTemplateAddQuestionView(LoginRequiredMixin, CreateView):
    model = AuditQuestion
    form_class = AuditQuestionForm
    template_name = "audits/template_add_question.html"

    def dispatch(self, request, *args, **kwargs):
        self.template_obj = get_object_or_404(AuditTemplate, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        next_sequence = (
            self.template_obj.questions.order_by("-sequence").values_list("sequence", flat=True).first() or 0
        ) + 1
        initial["sequence"] = next_sequence
        return initial

    def form_valid(self, form):
        form.instance.template = self.template_obj
        response = super().form_valid(form)
        messages.success(self.request, "Audit question added to the template.")
        return response

    def get_success_url(self):
        return reverse("audits:template_detail", kwargs={"pk": self.template_obj.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template"] = self.template_obj
        return context


class AuditTemplateAddQuestionsView(LoginRequiredMixin, TemplateView):
    template_name = "audits/template_add_questions.html"

    def dispatch(self, request, *args, **kwargs):
        self.template_obj = get_object_or_404(AuditTemplate, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def _get_next_sequence(self):
        return (self.template_obj.questions.order_by("-sequence").values_list("sequence", flat=True).first() or 0) + 1

    def get_formset(self):
        if self.request.method == "POST":
            return AuditQuestionFormSet(self.request.POST, queryset=AuditQuestion.objects.none())
        formset = AuditQuestionFormSet(queryset=AuditQuestion.objects.none())
        next_sequence = self._get_next_sequence()
        for index, form in enumerate(formset.forms):
            form.initial["sequence"] = next_sequence + index
        return formset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template"] = self.template_obj
        context["formset"] = kwargs.get("formset", self.get_formset())
        return context

    def post(self, request, *args, **kwargs):
        formset = self.get_formset()
        if formset.is_valid():
            saved_count = 0
            next_sequence = self._get_next_sequence()
            for form in formset:
                if not form.cleaned_data or not form.cleaned_data.get("question_text"):
                    continue
                question = form.save(commit=False)
                question.template = self.template_obj
                if not question.sequence:
                    question.sequence = next_sequence + saved_count
                question.save()
                saved_count += 1

            if saved_count:
                messages.success(request, f"{saved_count} audit questions added to the template.")
                return redirect("audits:template_detail", pk=self.template_obj.pk)
            messages.error(request, "Add at least one question before saving.")

        return self.render_to_response(self.get_context_data(formset=formset))


class AuditTemplateRemoveQuestionView(LoginRequiredMixin, TemplateView):
    template_name = "audits/template_remove_question.html"

    def dispatch(self, request, *args, **kwargs):
        self.template_obj = get_object_or_404(AuditTemplate, pk=kwargs["template_pk"])
        self.question = get_object_or_404(AuditQuestion, pk=kwargs["question_pk"], template=self.template_obj)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template"] = self.template_obj
        context["question"] = self.question
        return context

    def post(self, request, *args, **kwargs):
        self.question.delete()
        messages.success(request, "Audit question removed from the template.")
        return redirect("audits:template_detail", pk=self.template_obj.pk)


class AuditScheduleListView(LoginRequiredMixin, ListView):
    model = AuditSchedule
    template_name = "audits/schedule_list.html"
    context_object_name = "schedules"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            AuditSchedule.objects.select_related(
                "template", "template__category", "auditor", "location", "location__zone", "location__zone__plant"
            )
            .prefetch_related("plants", "zones", "locations", "sublocations")
            .annotate(
                open_findings=Count(
                    "findings",
                    filter=Q(
                        findings__status__in=[
                            AuditFinding.STATUS_DRAFT,
                            AuditFinding.STATUS_OPEN,
                            AuditFinding.STATUS_IN_PROGRESS,
                        ],
                        findings__is_archived=False,
                    ),
                )
            )
            .order_by("-scheduled_date", "-created_at")
        )
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "").strip()
        priority = self.request.GET.get("priority", "").strip()
        category_id = self.request.GET.get("category", "").strip()
        auditor_id = self.request.GET.get("auditor", "").strip()

        if search:
            queryset = queryset.filter(
                Q(schedule_code__icontains=search)
                | Q(template__title__icontains=search)
                | Q(auditor__first_name__icontains=search)
                | Q(auditor__last_name__icontains=search)
                | Q(location__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category_id:
            queryset = queryset.filter(template__category_id=category_id)
        if auditor_id:
            queryset = queryset.filter(auditor_id=auditor_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedules = self.get_queryset()
        context["total_audits"] = schedules.count()
        context["in_progress_count"] = schedules.filter(status=AuditSchedule.STATUS_IN_PROGRESS).count()
        context["total_open_findings"] = sum(schedule.open_findings for schedule in schedules)
        context["search"] = self.request.GET.get("search", "").strip()
        context["selected_status"] = self.request.GET.get("status", "").strip()
        context["selected_priority"] = self.request.GET.get("priority", "").strip()
        context["selected_category"] = self.request.GET.get("category", "").strip()
        context["selected_auditor"] = self.request.GET.get("auditor", "").strip()
        context["categories"] = AuditCategory.objects.filter(is_active=True).order_by("category_name")
        context["auditors"] = User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")
        context["status_choices"] = AuditSchedule.STATUS_CHOICES
        context["priority_choices"] = AuditSchedule.PRIORITY_CHOICES
        return context


class AuditScheduleCreateView(LoginRequiredMixin, CreateView):
    model = AuditSchedule
    form_class = AuditScheduleForm
    template_name = "audits/schedule_form.html"

    def get_initial(self):
        initial = super().get_initial()
        template_id = self.request.GET.get("template")
        if template_id:
            initial["template"] = template_id
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = AuditSchedule.STATUS_SCHEDULED
        self.object.save()
        form.save_related_locations(self.object)
        messages.success(self.request, f"Audit schedule {self.object.schedule_code} created successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("audits:schedule_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Schedule Audit"
        context["action"] = "Create"
        return context


class AuditScheduleDetailView(LoginRequiredMixin, DetailView):
    model = AuditSchedule
    template_name = "audits/schedule_detail.html"
    context_object_name = "schedule"

    def get_queryset(self):
        return (
            AuditSchedule.objects.select_related(
                "template", "template__category", "auditor", "location", "location__zone", "location__zone__plant"
            )
            .prefetch_related(
                "plants",
                "zones",
                "locations",
                "sublocations",
                Prefetch("responses", queryset=AuditResponse.objects.select_related("question")),
                Prefetch("findings", queryset=AuditFinding.objects.filter(is_archived=False).prefetch_related("capas")),
            )
        )


class AuditExecuteView(AuditorOrAdminRequiredMixin, View):
    template_name = "audits/audit_execute.html"

    def get_schedule(self):
        return get_object_or_404(
            AuditSchedule.objects.select_related(
                "template", "template__category", "auditor", "location", "location__zone", "location__zone__plant"
            ).prefetch_related("template__questions", "findings", "plants", "zones", "locations", "sublocations"),
            pk=self.kwargs["pk"],
        )

    def dispatch(self, request, *args, **kwargs):
        self.schedule = self.get_schedule()
        if request.user != self.schedule.auditor and not _is_auditor_or_admin(request.user):
            messages.error(request, "Only the assigned Auditor or an Admin can start this audit.")
            return redirect("audits:schedule_detail", pk=self.schedule.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.schedule.status in [AuditSchedule.STATUS_DRAFT, AuditSchedule.STATUS_SCHEDULED]:
            self.schedule.status = AuditSchedule.STATUS_IN_PROGRESS
            self.schedule.started_at = self.schedule.started_at or timezone.now()
            self.schedule.save(update_fields=["status", "started_at", "updated_at"])

        questions = list(self.schedule.template.questions.all())
        formset = AuditExecutionFormSet(initial=_build_execution_initial(self.schedule))
        return self.render_response(formset, questions)

    def post(self, request, *args, **kwargs):
        questions = list(self.schedule.template.questions.all())
        initial = _build_execution_initial(self.schedule)
        formset = AuditExecutionFormSet(request.POST, request.FILES, initial=initial)

        if formset.is_valid():
            archive_confirmation_missing = False
            for index, form in enumerate(formset.forms):
                question = questions[index]
                data = form.cleaned_data
                previous_status = data.get("previous_status")
                if previous_status == AuditResponse.STATUS_FAIL and data["status"] != AuditResponse.STATUS_FAIL:
                    existing_finding = AuditFinding.objects.filter(
                        parent_audit=self.schedule,
                        origin_question=question,
                        is_archived=False,
                    ).first()
                    if existing_finding and not data.get("archive_finding"):
                        archive_confirmation_missing = True
                        form.add_error(
                            "archive_finding",
                            "Tick this box to archive the linked finding before changing Fail to Pass/N/A.",
                        )

            if not archive_confirmation_missing:
                try:
                    with transaction.atomic():
                        for index, form in enumerate(formset.forms):
                            question = questions[index]
                            data = form.cleaned_data
                            response, _ = AuditResponse.objects.get_or_create(
                                schedule=self.schedule,
                                question=question,
                                defaults={"status": data["status"]},
                            )

                            previous_status = data.get("previous_status") or response.status
                            response.status = data["status"]
                            response.comment = data.get("comment", "")
                            if data.get("photo_evidence"):
                                response.photo_evidence = data["photo_evidence"]
                            response.save()

                            existing_finding = AuditFinding.objects.filter(
                                parent_audit=self.schedule,
                                origin_question=question,
                                is_archived=False,
                            ).first()

                            if previous_status == AuditResponse.STATUS_FAIL and data["status"] != AuditResponse.STATUS_FAIL:
                                if existing_finding and data.get("archive_finding"):
                                    existing_finding.archive(
                                        "Response updated from Fail to a compliant state during audit execution."
                                    )

                            if data["status"] == AuditResponse.STATUS_FAIL:
                                finding = AuditFinding.objects.get(parent_audit=self.schedule, origin_question=question)
                                finding.observation_detail = (
                                    data.get("observation_detail") or response.comment or question.question_text
                                )
                                finding.risk_score = data.get("risk_score") or finding.risk_score
                                if finding.manager_review_status == AuditFinding.REVIEW_REJECTED:
                                    finding.manager_review_status = AuditFinding.REVIEW_PENDING
                                    finding.status = AuditFinding.STATUS_DRAFT
                                finding.save()

                        action = request.POST.get("action")
                        self.schedule.status = (
                            AuditSchedule.STATUS_COMPLETED if action == "complete" else AuditSchedule.STATUS_IN_PROGRESS
                        )
                        self.schedule.completed_at = timezone.now() if action == "complete" else None
                        self.schedule.save()
                except Exception as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(
                        request,
                        "Audit saved successfully." if request.POST.get("action") != "complete" else "Audit completed successfully.",
                    )
                    return redirect("audits:schedule_detail", pk=self.schedule.pk)

        return self.render_response(formset, questions)

    def render_response(self, formset, questions):
        from django.shortcuts import render

        return render(
            self.request,
            self.template_name,
            {
                "schedule": self.schedule,
                "formset": formset,
                "question_forms": zip(questions, formset.forms),
            },
        )


class AuditFindingDashboardView(LoginRequiredMixin, ListView):
    model = AuditFinding
    template_name = "audits/finding_dashboard.html"
    context_object_name = "findings"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            AuditFinding.objects.filter(
                is_archived=False,
                status__in=[AuditFinding.STATUS_OPEN, AuditFinding.STATUS_IN_PROGRESS],
            )
            .select_related("parent_audit", "origin_question", "parent_audit__location", "parent_audit__auditor")
            .prefetch_related("capas")
            .order_by("-created_at")
        )
        search = self.request.GET.get("search", "").strip()
        status = self.request.GET.get("status", "").strip()
        risk = self.request.GET.get("risk", "").strip()
        priority = self.request.GET.get("priority", "").strip()

        if search:
            queryset = queryset.filter(
                Q(finding_id__icontains=search)
                | Q(parent_audit__schedule_code__icontains=search)
                | Q(origin_question__question_text__icontains=search)
                | Q(observation_detail__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if risk:
            queryset = queryset.filter(risk_score=risk)
        if priority:
            queryset = queryset.filter(parent_audit__priority=priority)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "").strip()
        context["selected_status"] = self.request.GET.get("status", "").strip()
        context["selected_risk"] = self.request.GET.get("risk", "").strip()
        context["selected_priority"] = self.request.GET.get("priority", "").strip()
        context["status_choices"] = [
            (AuditFinding.STATUS_OPEN, "Open"),
            (AuditFinding.STATUS_IN_PROGRESS, "In-Progress"),
        ]
        context["risk_choices"] = AuditFinding.RISK_CHOICES
        context["priority_choices"] = AuditSchedule.PRIORITY_CHOICES
        return context


class AuditFindingDetailView(LoginRequiredMixin, DetailView):
    model = AuditFinding
    template_name = "audits/finding_detail.html"
    context_object_name = "finding"

    def get_queryset(self):
        return AuditFinding.objects.select_related(
            "parent_audit",
            "parent_audit__template",
            "origin_question",
            "reviewed_by",
        ).prefetch_related("capas__assigned_to")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["response"] = AuditResponse.objects.filter(
            schedule=self.object.parent_audit,
            question=self.object.origin_question,
        ).first()
        context["capa_form"] = CAPACreateForm()
        return context


class AuditFindingReviewView(ManagerOrAdminRequiredMixin, UpdateView):
    model = AuditFinding
    form_class = AuditFindingReviewForm
    template_name = "audits/finding_review.html"
    context_object_name = "finding"

    def form_valid(self, form):
        finding = form.save(commit=False)
        finding.reviewed_by = self.request.user
        finding.reviewed_at = timezone.now()
        finding.manager_review_status = form.cleaned_data["decision"]
        finding.status = (
            AuditFinding.STATUS_OPEN
            if form.cleaned_data["decision"] == AuditFinding.REVIEW_APPROVED
            else AuditFinding.STATUS_DRAFT
        )
        finding.save()
        messages.success(self.request, f"Finding {finding.finding_id} reviewed successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("audits:finding_detail", kwargs={"pk": self.object.pk})


class CAPACreateView(ManagerOrAdminRequiredMixin, CreateView):
    model = CAPA
    form_class = CAPACreateForm
    template_name = "audits/capa_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.finding = get_object_or_404(AuditFinding, pk=kwargs["finding_pk"], is_archived=False)
        if self.finding.manager_review_status != AuditFinding.REVIEW_APPROVED:
            messages.error(request, "Approve the finding before opening a CAPA task.")
            return redirect("audits:finding_detail", pk=self.finding.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.finding = self.finding
        response = super().form_valid(form)
        self.finding.status = AuditFinding.STATUS_IN_PROGRESS
        self.finding.save(update_fields=["status", "updated_at"])
        messages.success(self.request, "CAPA task created successfully.")
        return response

    def get_success_url(self):
        return reverse("audits:finding_detail", kwargs={"pk": self.finding.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["finding"] = self.finding
        return context


class CAPAUpdateView(LoginRequiredMixin, UpdateView):
    model = CAPA
    form_class = CAPAUpdateForm
    template_name = "audits/capa_update.html"
    context_object_name = "capa"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.assigned_to and not _is_manager_or_admin(request.user):
            messages.error(request, "Only the action owner or an Admin/Manager can update this CAPA.")
            return redirect("audits:finding_detail", pk=self.object.finding.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return CAPA.objects.select_related("finding", "assigned_to", "finding__parent_audit")

    def form_valid(self, form):
        capa = form.save(commit=False)
        if form.cleaned_data.get("mark_as_fixed"):
            capa.verification_status = CAPA.STATUS_FIXED
        capa.save()

        if capa.verification_status == CAPA.STATUS_FIXED:
            capa.finding.status = AuditFinding.STATUS_RESOLVED
            capa.finding.save(update_fields=["status", "updated_at"])
        elif capa.verification_status == CAPA.STATUS_VERIFIED:
            capa.verified_by = self.request.user
            capa.verified_at = timezone.now()
            capa.save(update_fields=["verified_by", "verified_at", "updated_at"])
            capa.finding.status = AuditFinding.STATUS_CLOSED
            capa.finding.save(update_fields=["status", "updated_at"])

        messages.success(self.request, "CAPA updated successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("audits:finding_detail", kwargs={"pk": self.object.finding.pk})
