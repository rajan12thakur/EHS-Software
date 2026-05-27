from django.contrib import admin

from .models import (LegalAct, ComplianceRequirement)


class ComplianceRequirementInline(admin.TabularInline):
    model = ComplianceRequirement
    extra = 0

    fields = [
        'requirement_code',
        'title',
        'frequency',
        'criticality',
        'is_active'
    ]

    readonly_fields = [
        'requirement_code'
    ]

    show_change_link = True


@admin.register(LegalAct)
class LegalActAdmin(admin.ModelAdmin):

    list_display = [
        'act_code',
        'act_name',
        'authority_name',
        'government_level',
        'category',
        'effective_date',
        'is_active',
    ]

    list_filter = [
        'government_level',
        'category',
        'is_active',
        'effective_date',
    ]

    search_fields = [
        'act_code',
        'act_name',
        'short_name',
        'authority_name',
    ]

    readonly_fields = [
        'act_code',
        'created_at',
        'updated_at',
    ]

    fieldsets = (

        ('Basic Information', {
            'fields': (
                'act_code',
                'act_name',
                'short_name',
                'authority_name',
            )
        }),

        ('Governance Information', {
            'fields': (
                'government_level',
                'category',
                'effective_date',
                'is_active',
            )
        }),

        ('Description', {
            'fields': (
                'description',
                'applicability_notes',
            )
        }),

        ('Audit Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            )
        }),
    )

    inlines = [ComplianceRequirementInline]

@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):

    list_display = [
        'requirement_code',
        'title',
        'legal_act',
        'frequency',
        'criticality',
        'get_responsible_persons',
        'get_reviewers',
        'is_active',
    ]

    list_filter = [
        'frequency',
        'criticality',
        'is_active',
        'requires_approval',
        'evidence_required',
    ]

    search_fields = [
        'requirement_code',
        'title',
        'legal_act__act_name',
    ]

    autocomplete_fields = [
        'legal_act',
    ]

    filter_horizontal = [
        'applicable_plants',
        'applicable_departments',
        'responsible_person',
        'reviewer',
    ]

    readonly_fields = [
        'requirement_code',
        'created_at',
        'updated_at',
    ]

    fieldsets = (

        ('Basic Information', {
            'fields': (
                'requirement_code',
                'title',
                'legal_act',
                'description',
            )
        }),

        ('Compliance Configuration', {
            'fields': (
                'frequency',
                'criticality',
            )
        }),

        ('Workflow Configuration', {
            'fields': (
                'evidence_required',
                'requires_approval',
                'due_days_before',
                'reminder_days',
                'escalation_days',
            )
        }),

        ('Applicability', {
            'fields': (
                'applicable_plants',
                'applicable_departments',
            )
        }),

        ('Responsibility Matrix', {
            'fields': (
                'responsible_person',
                'reviewer',
            )
        }),

        ('Status', {
            'fields': (
                'is_active',
            )
        }),

        ('Audit Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            )
        }),
    )

    def get_responsible_persons(self, obj):

        return ", ".join([
            user.get_full_name() or user.username
            for user in obj.responsible_person.all()
        ])

    get_responsible_persons.short_description = (
        'Responsible Persons'
    )

    def get_reviewers(self, obj):

        return ", ".join([
            user.get_full_name() or user.username
            for user in obj.reviewer.all()
        ])

    get_reviewers.short_description = (
        'Reviewers'
    )
