from django.urls import path

from .views import (
    toolbox_category_create,
    toolbox_category_list,
    toolbox_category_update,
    toolbox_category_delete,
)

app_name = 'toolbox_talk'


urlpatterns = [

    # Toolbox Talk Category URLs
    path('categories/',toolbox_category_list,name='toolbox_category_list'),
    path('categories/create/',toolbox_category_create,name='toolbox_category_create'),
    path('categories/update/<int:pk>/',toolbox_category_update,name='toolbox_category_update'),
    path('categories/delete/<int:pk>/',toolbox_category_delete,name='toolbox_category_delete'),

]

