from django.urls import path
from .views import *

app_name = 'chemicals'

urlpatterns = [
    path('create/', ChemicalCreateView.as_view(), name='chemical_create'),
    path('detail/<int:pk>/', ChemicalDetailView.as_view(), name='chemical_detail'),
    path('edit/<int:pk>/', ChemicalUpdateView.as_view(), name='chemical_edit'),
    path('list/', ChemicalListView.as_view(), name='chemical_list'),
    path('requests/create/', ChemicalRequestCreateView.as_view(), name='chemical_request_create'),
    path('approvals/', ChemicalApprovalDashboardView.as_view(), name='chemical_approvals'),
    path('requests/<int:pk>/approve/', ChemicalRequestApproveView.as_view(), name='chemical_request_approve'),
    path('requests/<int:pk>/reject/', ChemicalRequestRejectView.as_view(), name='chemical_request_reject'),
]
