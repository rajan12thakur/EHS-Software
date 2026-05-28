from django.urls import path
from . import views

app_name = 'legal_compliance'


urlpatterns = [

    # =====================================================
    # DASHBOARD
    # =====================================================
    path('dashboard/', views.LegalComplianceDashboardView.as_view(),name='dashboard'),

    # =====================================================
    # LEGAL ACTS
    # =====================================================
    path('acts/',views.LegalActListView.as_view(),name='act_list'),
    path('acts/create/',views.LegalActCreateView.as_view(),name='act_create'),
    path('acts/<int:pk>/',views.LegalActDetailView.as_view(),name='act_detail'),
    path('acts/<int:pk>/edit/',views.LegalActUpdateView.as_view(),name='act_edit'),
    path('acts/<int:pk>/delete/',views.LegalActDeleteView.as_view(),name='act_delete'),


    # ====================================
    # COMPLIANCE QUESTIONS
    # ====================================

    path('questions/',views.compliance_question_list,name='question_list'),
    path('questions/create/',views.compliance_question_create,name='question_create'),
    path('questions/<int:pk>/',views.compliance_question_detail,name='question_detail'),
    path('questions/<int:pk>/edit/',views.compliance_question_edit,name='question_edit'),
    path('questions/<int:pk>/delete/',views.compliance_question_delete,name='question_delete'),

    # =====================================================
    # COMPLIANCE complianceS
    # =====================================================
    path('compliances/',views.ComplianceRequirementListView.as_view(),name='compliance_list'),
    path('compliances/create/',views.ComplianceRequirementCreateView.as_view(),name='compliance_create'),
    path('compliances/<int:pk>/',views.ComplianceRequirementDetailView.as_view(),name='compliance_detail'),
    path('compliances/<int:pk>/edit/',views.ComplianceRequirementUpdateView.as_view(),name='compliance_edit'),
    path('compliances/<int:pk>/delete/',views.ComplianceRequirementDeleteView.as_view(),name='compliance_delete'),

    # =====================================================
    # MY COMPLIANCES
    # =====================================================
    path('my-compliances/',views.my_compliances,name='my_compliances'),
    path('start/<int:requirement_id>/',views.compliance_start,name='compliance_start'),
    path('submit/<int:requirement_id>/',views.compliance_submit,name='compliance_submit'),
    path('review/<int:submission_id>/',views.compliance_review,name='compliance_review'),

    # # =====================================================
    # # COMPLIANCE Calendar Dashboard
    # # =====================================================
    path('compliance-calendar/',views.compliance_calendar_dashboard,name='compliance_calendar_dashboard'),

    # =====================================================
    # COMPLIANCE Audit Report
    # =====================================================
    path('reports/status/',views.ComplianceStatusReportView.as_view(),name='status_report'),
    path('reports/status/excel/',views.export_compliance_status_excel,name='export_status_excel'),
    path('reports/status/pdf/',views.export_compliance_status_pdf,name='export_status_pdf'),
    path('reports/overdue/',views.OverdueComplianceDashboardView.as_view(),name='overdue_dashboard'),
    
    # # =====================================================
    # # COMPLIANCE Governance Score
    # # =====================================================
    # path('governance-score/',views.ComplianceGovernanceScoreView.as_view(),name='governance_score'),


    # =====================================================
    # Other Calling
    # =====================================================
    path('ajax/get-users-by-plants/',views.get_users_by_plants,name='get_users_by_plants'),
    path('ajax/get-reviewers/',views.get_reviewers,name='get_reviewers'),

    # =====================================================
    # CAPA
    # =====================================================
    path('my-findings/',views.my_findings,name='my_findings'),
    path('findings/<int:pk>/',views.finding_detail,name='finding_detail'),
    path('my-notices/',views.my_regulatory_notices,name='my_regulatory_notices'),
    path('notices/<int:pk>/',views.notice_detail,name='notice_detail'),
    path('notices/create/',views.RegulatoryNoticeCreateView.as_view(),name='notice_create'),

    # =====================================================
    # Notifications System 
    # =====================================================
    path('notifications/',views.notifications,name='notifications'),
]