from django.contrib import admin

from .models import AuditCategory, AuditFinding, AuditQuestion, AuditResponse, AuditSchedule, AuditTemplate, CAPA


@admin.register(AuditCategory)
class AuditCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "category_code", "is_active", "created_by")
    list_filter = ("is_active",)
    search_fields = ("category_name", "category_code", "description")


class AuditQuestionInline(admin.TabularInline):
    model = AuditQuestion
    extra = 1


@admin.register(AuditTemplate)
class AuditTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "category", "standard_reference")
    list_filter = ("category",)
    search_fields = ("title", "version", "standard_reference", "category__category_name", "category__category_code")
    inlines = [AuditQuestionInline]


@admin.register(AuditSchedule)
class AuditScheduleAdmin(admin.ModelAdmin):
    list_display = ("schedule_code", "template", "auditor", "location", "scheduled_date", "priority", "status")
    list_filter = ("status", "priority", "template__category", "scheduled_date")
    search_fields = ("schedule_code", "template__title", "auditor__username", "location__name")


@admin.register(AuditResponse)
class AuditResponseAdmin(admin.ModelAdmin):
    list_display = ("schedule", "question", "status", "answered_at")
    list_filter = ("status", "question__template")
    search_fields = ("schedule__schedule_code", "question__question_text", "comment")


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ("finding_id", "parent_audit", "risk_score", "status", "manager_review_status", "is_archived")
    list_filter = ("risk_score", "status", "manager_review_status", "is_archived")
    search_fields = ("finding_id", "observation_detail", "origin_question__question_text")


@admin.register(CAPA)
class CAPAAdmin(admin.ModelAdmin):
    list_display = ("finding", "assigned_to", "due_date", "verification_status")
    list_filter = ("verification_status", "due_date")
    search_fields = ("finding__finding_id", "action_required", "assigned_to__username")
