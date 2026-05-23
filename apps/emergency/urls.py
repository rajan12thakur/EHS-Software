from django.urls import path

from . import views

app_name = "emergency"

urlpatterns = [
    path("", views.EmergencyHomeView.as_view(), name="home"),
    path("reports/", views.EmergencyReportListView.as_view(), name="report_list"),
    path("reports/create/", views.EmergencyReportCreateView.as_view(), name="report_create"),
    path("reports/<int:pk>/", views.EmergencyReportDetailView.as_view(), name="report_detail"),
    path("reports/<int:report_pk>/investigation/create/", views.EmergencyInvestigationCreateView.as_view(), name="investigation_create"),
    path("investigations/<int:pk>/", views.EmergencyInvestigationDetailView.as_view(), name="investigation_detail"),
    path("my-action-items/", views.EmergencyMyActionItemsView.as_view(), name="my_action_items"),
    path("action-items/<int:pk>/complete/", views.EmergencyActionItemCompleteView.as_view(), name="action_item_complete"),
    path("contact-directory/", views.ContactDirectoryView.as_view(), name="contact_directory"),
    path("questions/", views.ERTQuestionListView.as_view(), name="question_list"),
    path("questions/create/", views.ERTQuestionCreateView.as_view(), name="question_create"),
    path("questions/<int:pk>/edit/", views.ERTQuestionUpdateView.as_view(), name="question_edit"),
    path("questions/<int:pk>/delete/", views.ERTQuestionDeleteView.as_view(), name="question_delete"),
    path("topics/", views.EmergencyTopicListView.as_view(), name="topic_list"),
    path("topics/create/", views.EmergencyTopicCreateView.as_view(), name="topic_create"),
    path("topics/<int:pk>/edit/", views.EmergencyTopicUpdateView.as_view(), name="topic_edit"),
    path("sessions/", views.EmergencySessionListView.as_view(), name="session_list"),
    path("sessions/create/", views.EmergencySessionCreateView.as_view(), name="session_create"),
    path("sessions/<int:pk>/",views.EmergencySessionDetailView.as_view(), name="session_detail"),
    path("sessions/<int:pk>/participants/add/", views.EmergencyAddParticipantsView.as_view(), name="add_participants"),
    path("my-sessions/", views.MyEmergencySessionsView.as_view(), name="my_sessions"),
    path("my-sessions/<int:participant_id>/start/", views.EmergencySessionStartView.as_view(), name="session_start"),
    path("my-sessions/<int:participant_id>/submit/", views.EmergencySessionSubmitView.as_view(), name="session_submit"),
    path("submissions/<int:submission_id>/review/", views.EmergencySubmissionReviewView.as_view(), name="submission_review"),
    path("ajax/get-zones/", views.EmergencyGetZonesAjaxView.as_view(), name="ajax_get_zones"),
    path("ajax/get-locations/", views.EmergencyGetLocationsAjaxView.as_view(), name="ajax_get_locations"),
    path("ajax/get-sublocations/", views.EmergencyGetSublocationsAjaxView.as_view(), name="ajax_get_sublocations"),
    path("ajax/department-users/", views.EmergencyDepartmentUsersAjaxView.as_view(), name="ajax_department_users"),
]
