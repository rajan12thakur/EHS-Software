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

        contractor_formset = PermitContractorFormSet(self.request.POST)
        attachment_formset = PermitAttachmentFormSet(
            self.request.POST,
            self.request.FILES
        )

        if contractor_formset.is_valid() and attachment_formset.is_valid():

            self.object = form.save(commit=False)

            # ✅ REQUIRED FIX (YOU MISSED THIS)
            self.object.requester_user = self.request.user
            self.object.requester_name = (
                self.request.user.get_full_name() or self.request.user.username
            )

            # Optional defaults
            if not self.object.plant:
                self.object.plant = self.request.user.plant

            if not self.object.department:
                self.object.department = self.request.user.department

            self.object.save()

            contractor_formset.instance = self.object
            contractor_formset.save()

            attachment_formset.instance = self.object
            attachment_formset.save()

            messages.success(self.request, "Permit created successfully.")
            return super().form_valid(form)

        messages.error(self.request, "Please correct the errors in contractors or attachments.")
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

class PermitUpdateView(LoginRequiredMixin, UpdateView):
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
        else:
            context['contractor_formset'] = PermitContractorFormSet(instance=self.object)
            context['attachment_formset'] = PermitAttachmentFormSet(instance=self.object)

        context['is_edit'] = True
        return context

    def form_valid(self, form):
        contractor_formset = PermitContractorFormSet(
            self.request.POST,
            instance=self.object
        )
        attachment_formset = PermitAttachmentFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )

        if contractor_formset.is_valid() and attachment_formset.is_valid():

            self.object = form.save()

            contractor_formset.save()
            attachment_formset.save()

            messages.success(self.request, "Permit updated successfully.")
            return super().form_valid(form)

        messages.error(self.request, "Please fix errors.")
        return self.form_invalid(form)