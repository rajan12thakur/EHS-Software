from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PermitType
from django.db.models import Q
from .forms import PermitForm, PermitContractorFormSet, PermitAttachmentFormSet

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