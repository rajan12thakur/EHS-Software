from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PermitType, Permit, PermitContractor, PermitAttachment
from django.db.models import Q
from .forms import PermitForm, PermitContractorFormSet, PermitAttachmentFormSet
from django.views.generic import ListView

# PERMIT TYPE LIST VIEW
class PermitTypeListView(LoginRequiredMixin, ListView):
    model = PermitType
    template_name = 'permit/permit_type_list.html'
    context_object_name = 'permit_types'
    paginate_by = 10

    def get_queryset(self):
        queryset = PermitType.objects.all().order_by('-created_at')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Permit Types'
        context['search_query'] = self.request.GET.get('search', '')
        context['active_count'] = PermitType.objects.filter(is_active=True).count()
        return context

# PERMIT TYPE CREATE VIEW
class PermitTypeCreateView(LoginRequiredMixin, CreateView):
    model = PermitType
    fields = ['name', 'code', 'description', 'is_active']
    template_name = 'permit/permit_type_form.html'
    success_url = reverse_lazy('permit:permit_type_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Permit Type created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


# PERMIT TYPE UPDATE VIEW
class PermitTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = PermitType
    fields = ['name', 'code', 'description', 'is_active']
    template_name = 'permit/permit_type_form.html'
    success_url = reverse_lazy('permit:permit_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Permit Type updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

# PERMIT TYPE DELETE VIEW
class PermitTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = PermitType
    template_name = 'permit/permit_type_confirm_delete.html'
    success_url = reverse_lazy('permit:permit_type_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Permit Type deleted successfully.")
        return super().delete(request, *args, **kwargs)

class PermitCreateView(LoginRequiredMixin, CreateView):
    model = Permit
    form_class = PermitForm
    template_name = 'permit/permit_create.html'
    success_url = reverse_lazy('permit:permit_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.method == "POST":
            context['contractor_formset'] = PermitContractorFormSet(
                self.request.POST
            )
            context['attachment_formset'] = PermitAttachmentFormSet(
                self.request.POST,
                self.request.FILES
            )
        else:
            context['contractor_formset'] = PermitContractorFormSet()
            context['attachment_formset'] = PermitAttachmentFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        contractor_formset = context['contractor_formset']
        attachment_formset = context['attachment_formset']

        if contractor_formset.is_valid() and attachment_formset.is_valid():

            self.object = form.save()

            contractor_formset.instance = self.object
            contractor_formset.save()

            # ✅ SAVE ONLY NON-EMPTY ATTACHMENTS
            attachments = attachment_formset.save(commit=False)

            for att in attachments:
                if att.file or att.description:
                    att.permit = self.object
                    att.save()

            return super().form_valid(form)

        return self.form_invalid(form)

class PermitListView(LoginRequiredMixin, ListView):
    model = Permit
    template_name = 'permit/permit_list.html'
    context_object_name = 'permits'
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Permit.objects
            .select_related(
                'permit_type',
                'plant',
                'zone',
                'location',
                'department',
                'requester_user'
            )
            .all()
            .order_by('-created_at')
        )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(permit_number__icontains=search) |
                Q(requester_name__icontains=search) |
                Q(job_description__icontains=search) |
                Q(contractor_company__icontains=search)
            )

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        permit_type = self.request.GET.get('permit_type')
        if permit_type:
            queryset = queryset.filter(permit_type_id=permit_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['status_choices'] = Permit.STATUS_CHOICES
        context['permit_types'] = (
            Permit.objects.values_list('permit_type__id', 'permit_type__name')
            .distinct()
        )

        context['filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'permit_type': self.request.GET.get('permit_type', ''),
        }

        return context

class PermitDetailView(LoginRequiredMixin, DetailView):
    model = Permit
    template_name = 'permit/permit_detail.html'
    context_object_name = 'permit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        permit = self.object

        context['contractors'] = permit.contractors.all()
        context['attachments'] = permit.attachments.all()
        context['logs'] = permit.approval_logs.all()

        context['cancel_url'] = reverse_lazy('permit:permit_list')

        return context

from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Permit
from .forms import PermitForm, PermitContractorFormSet, PermitAttachmentFormSet


class PermitUpdateView(LoginRequiredMixin, UpdateView):
    model = Permit
    form_class = PermitForm
    template_name = 'permit/permit_edit.html'
    success_url = reverse_lazy('permit:permit_list')

    # ✅ Pass user to form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # ✅ Context (Formsets + hazards)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['contractor_formset'] = PermitContractorFormSet(
                self.request.POST,
                instance=self.object
            )
            context['attachment_formset'] = PermitAttachmentFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )

            # ✅ hazards from POST
            context['selected_hazards'] = self.request.POST.getlist('hazards')

        else:
            context['contractor_formset'] = PermitContractorFormSet(
                instance=self.object
            )
            context['attachment_formset'] = PermitAttachmentFormSet(
                instance=self.object
            )

            # ✅ hazards from DB
            context['selected_hazards'] = self.object.hazards or []

        return context

    # ✅ MAIN SAVE LOGIC
    def form_valid(self, form):
        context = self.get_context_data()
        contractor_formset = context['contractor_formset']
        attachment_formset = context['attachment_formset']

        # ✅ Validate all together
        if not contractor_formset.is_valid() or not attachment_formset.is_valid():
            return self.form_invalid(form)

        # ✅ SAVE hazards explicitly (IMPORTANT)
        form.instance.hazards = self.request.POST.getlist('hazards')

        # ✅ Save main object
        self.object = form.save()

        # ============================
        # ✅ CONTRACTORS
        # ============================
        contractor_formset.instance = self.object

        contractors = contractor_formset.save(commit=False)

        for c in contractors:
            # ✅ Ignore empty rows
            if any([
                c.name,
                c.trade,
                c.id_number,
                c.esi_number,
                c.contact_number
            ]):
                c.permit = self.object
                c.save()

        # ✅ Delete removed rows
        for obj in contractor_formset.deleted_objects:
            obj.delete()

        # ============================
        # ✅ ATTACHMENTS
        # ============================
        attachment_formset.instance = self.object

        attachments = attachment_formset.save(commit=False)

        for att in attachments:
            # ✅ Save only meaningful rows
            if att.file or att.description:
                att.permit = self.object
                att.save()

        # ✅ Delete removed attachments
        for obj in attachment_formset.deleted_objects:
            obj.delete()

        return super().form_valid(form)