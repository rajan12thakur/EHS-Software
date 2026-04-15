from django.urls import path
from .views import *

app_name = 'permit'

urlpatterns = [
    # Configuration URLs
    path('permit-types/', PermitTypeListView.as_view(), name='permit_type_list'),
    path('permit-types/create/', PermitTypeCreateView.as_view(), name='permit_type_create'),
    path('permit-types/<int:pk>/edit/', PermitTypeUpdateView.as_view(), name='permit_type_update'),
    path('permit-types/<int:pk>/delete/', PermitTypeDeleteView.as_view(), name='permit_type_delete'),

    # Permit URLs
    path('permits/create/', PermitCreateView.as_view(), name='permit_create'),
    path('permits/permit-list/', PermitListView.as_view(), name='permit_list'),
    path('permits/<int:pk>/', PermitDetailView.as_view(), name='permit_detail'),
    path('permits/<int:pk>/edit/', PermitUpdateView.as_view(), name='permit_update'),
]
