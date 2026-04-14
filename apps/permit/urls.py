from django.urls import path
from .views import PermitTypeListView, PermitTypeCreateView, PermitTypeUpdateView, PermitTypeDeleteView

app_name = 'permit'

urlpatterns = [
    # Configuration URLs
    path('permit-types/', PermitTypeListView.as_view(), name='permit_type_list'),
    path('permit-types/create/', PermitTypeCreateView.as_view(), name='permit_type_create'),
    path('permit-types/<int:pk>/edit/', PermitTypeUpdateView.as_view(), name='permit_type_update'),
    path('permit-types/<int:pk>/delete/', PermitTypeDeleteView.as_view(), name='permit_type_delete'),
]
