from django.urls import path
from . import views

app_name = 'audits'

urlpatterns = [
    path("categories/", views.AuditCategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.AuditCategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.AuditCategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.AuditCategoryDeleteView.as_view(), name="category_delete"),
    path("templates/", views.AuditTemplateListView.as_view(), name="template_list"),
    path("templates/create/", views.AuditTemplateCreateView.as_view(), name="template_create"),
    path("templates/<int:pk>/", views.AuditTemplateDetailView.as_view(), name="template_detail"),
    path("templates/<int:pk>/add-question/", views.AuditTemplateAddQuestionView.as_view(), name="template_add_question"),
    path("templates/<int:pk>/add-questions/", views.AuditTemplateAddQuestionsView.as_view(), name="template_add_questions"),
    path("templates/<int:template_pk>/remove-question/<int:question_pk>/", views.AuditTemplateRemoveQuestionView.as_view(), name="template_remove_question"),
    path("schedules/", views.AuditScheduleListView.as_view(), name="schedule_list"),
    path("schedules/create/", views.AuditScheduleCreateView.as_view(), name="schedule_create"),
    path("schedules/<int:pk>/", views.AuditScheduleDetailView.as_view(), name="schedule_detail"),
    path("schedules/<int:pk>/execute/", views.AuditExecuteView.as_view(), name="audit_execute"),
    path("findings/", views.AuditFindingDashboardView.as_view(), name="finding_dashboard"),
    path("findings/<int:pk>/", views.AuditFindingDetailView.as_view(), name="finding_detail"),
    path("findings/<int:pk>/review/", views.AuditFindingReviewView.as_view(), name="finding_review"),
    path("findings/<int:finding_pk>/capa/create/", views.CAPACreateView.as_view(), name="capa_create"),
    path("capa/<int:pk>/update/", views.CAPAUpdateView.as_view(), name="capa_update"),
]
