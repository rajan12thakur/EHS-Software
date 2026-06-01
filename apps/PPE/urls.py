from django.urls import path
from . import views

app_name = 'PPE'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/create', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('master-list/', views.master_list, name='master_list'),
    path('master-create/', views.create_ppe, name='create_ppe'),
    path('ppe/<int:pk>/', views.ppe_detail, name='ppe_detail'),
    path('ppe/<int:pk>/delete', views.ppe_delete, name='ppe_delete'),
    path('ppe/<int:pk>/edit', views.master_edit, name='master_edit'),
]