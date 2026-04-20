from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, DetailView, UpdateView

from .forms import ChemicalForm, ChemicalRequestApprovalForm, ChemicalRequestForm
from .models import Chemical, ChemicalRequest
from .utils import *


class ChemicalCreateView(LoginRequiredMixin, CreateView):
    model = Chemical
    form_class = ChemicalForm
    template_name = 'chemicals/chemical_form.html'
    success_url = reverse_lazy('chemicals:chemical_list')


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Chemical created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

class ChemicalDetailView(LoginRequiredMixin, DetailView):
    model = Chemical
    template_name = 'chemicals/chemical_detail.html'
    context_object_name = 'chemical'

    def get_queryset(self):
        return (
            Chemical.objects.select_related(
                'plant',
                'zone',
                'location',
                'sublocation',
                'department',
                'created_by'
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chemical = self.object

        ehs = chemical.ehs_compliance or {}

        context["ghs_list"] = ehs.get("ghs", [])
        context["ppe_list"] = ehs.get("ppe", [])

        return context

class ChemicalUpdateView(LoginRequiredMixin, UpdateView):
    model = Chemical
    form_class = ChemicalForm
    template_name = 'chemicals/chemical_edit.html'
    success_url = reverse_lazy('chemicals:chemical_list')

    def get_form_kwagrs(self):
        kwargs = super().get_form_kwargs()
        kwargs['files'] = self.request.FILES or None

    def form_valid(self, form):
        messages.success(self.request, "Chemical updated successfully.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['chemical'] = self.object

        return context

class ChemicalListView(LoginRequiredMixin, ListView):
    model = Chemical
    template_name = 'chemicals/chemical_list.html'
    context_object_name = 'chemicals'
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Chemical.objects.select_related(
                'plant',
                'zone',
                'location',
                'sublocation',
                'department',
                'created_by',
            )
            .all()
            .order_by('-created_at')
        )

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(chemical_name__icontains=search)
                | Q(trade_name__icontains=search)
                | Q(cas_number__icontains=search)
                | Q(supplier__icontains=search)
            )

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Chemical.STATUS_CHOICES
        context['filters'] = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
        }
        context['total_chemicals'] = Chemical.objects.count()
        context['pending_requests'] = ChemicalRequest.objects.filter(status='pending').count()
        context['approved_requests'] = ChemicalRequest.objects.filter(status='approved').count()
        return context


class ChemicalRequestCreateView(LoginRequiredMixin, CreateView):
    model = ChemicalRequest
    form_class = ChemicalRequestForm
    template_name = 'chemicals/chemical_request_form.html'
    success_url = reverse_lazy('chemicals:chemical_approvals')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Chemical request submitted successfully and is pending for approval.",
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class ChemicalApprovalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'chemicals/chemical_approval_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = ChemicalRequest.objects.select_related(
            'plant',
            'zone',
            'location',
            'sublocation',
            'department',
            'requester_user',
            'approved_by',
            'chemical',
        ).order_by('-created_at')

        pending_requests = list(base_qs.filter(status='pending'))
        approved_requests = list(base_qs.filter(status='approved'))
        rejected_requests = list(base_qs.filter(status='rejected'))

        context.update(
            {
                'pending_requests': pending_requests,
                'approved_requests': approved_requests,
                'rejected_requests': rejected_requests,
                'pending_count': len(pending_requests),
                'approved_count': len(approved_requests),
                'rejected_count': len(rejected_requests),
                'approval_chemical_choices': Chemical.objects.order_by('chemical_name'),
            }
        )
        return context


class ChemicalRequestApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chemical_request = get_object_or_404(ChemicalRequest, pk=pk)

        if chemical_request.status != 'pending':
            messages.error(request, "Only pending requests can be approved.")
            return redirect('chemicals:chemical_approvals')

        form = ChemicalRequestApprovalForm(
            {
                'status': 'approved',
                'chemical': request.POST.get('chemical'),
                'rejection_reason': '',
            },
            instance=chemical_request,
            approver=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Chemical request approved successfully.")
        else:
            messages.error(
                request,
                form.errors.get('__all__', ['Unable to approve the chemical request.'])[0],
            )

        return redirect('chemicals:chemical_approvals')


class ChemicalRequestRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chemical_request = get_object_or_404(ChemicalRequest, pk=pk)

        if chemical_request.status != 'pending':
            messages.error(request, "Only pending requests can be rejected.")
            return redirect('chemicals:chemical_approvals')

        form = ChemicalRequestApprovalForm(
            {
                'status': 'rejected',
                'chemical': '',
                'rejection_reason': request.POST.get('rejection_reason', '').strip(),
            },
            instance=chemical_request,
            approver=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Chemical request rejected successfully.")
        else:
            error_message = form.errors.get(
                'rejection_reason',
                form.errors.get('__all__', ['Unable to reject the chemical request.']),
            )[0]
            messages.error(request, error_message)

        return redirect('chemicals:chemical_approvals')

class ChemicalPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        chemical = get_object_or_404(
            Chemical.objects.select_related(
                'plant',
                'zone',
                'location',
                'sublocation',
                'department',
                'created_by',
            ),
            pk=pk
        )

        return generate_chemical_pdf(chemical)