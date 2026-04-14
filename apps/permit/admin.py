from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (PermitType,Permit,PermitContractor,PermitApprovalLog,PermitExtension,PermitAttachment,)


STATUS_COLORS = {
    'draft':      '#9e9e9e',
    'pending':    '#ff9800',
    'approved':   '#2196f3',
    'rejected':   '#f44336',
    'active':     '#4caf50',
    'closed':     '#607d8b',
    'reapproval': '#ff5722',
}

PRIORITY_COLORS = {
    'low':       '#8bc34a',
    'medium':    '#ff9800',
    'high':      '#f44336',
    'emergency': '#9c27b0',
}


def colored_badge(text, color):
    return format_html(
        '<span style="background:{};color:#fff;padding:3px 10px;'
        'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
        color,
        text,
    )


# PERMIT TYPE
@admin.register(PermitType)
class PermitTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'permit_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Permits')
    def permit_count(self, obj):
        return obj.permits.count()


class PermitContractorInline(admin.TabularInline):
    model = PermitContractor
    extra = 1
    fields = ('name', 'trade', 'id_number', 'esi_number', 'contact_number')


class PermitAttachmentInline(admin.TabularInline):
    model = PermitAttachment
    extra = 0
    fields = ('file', 'description', 'original_filename', 'file_size', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('original_filename', 'file_size', 'uploaded_by', 'uploaded_at')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.uploaded_by_id:
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()


class PermitApprovalLogInline(admin.TabularInline):
    model = PermitApprovalLog
    extra = 0
    fields = ('timestamp', 'action', 'from_status', 'to_status', 'performed_by', 'comments')
    readonly_fields = ('timestamp', 'action', 'from_status', 'to_status', 'performed_by', 'comments')
    can_delete = False
    ordering = ('timestamp',)

    def has_add_permission(self, request, obj=None):
        return False


class PermitExtensionInline(admin.StackedInline):
    model = PermitExtension
    extra = 0
    fields = (
        ('original_end_date', 'new_end_date'),
        'reason',
        ('status', 'reviewed_by', 'reviewed_at'),
        'review_comments',
    )
    readonly_fields = ('original_end_date', 'reviewed_at')


# PERMIT
@admin.register(Permit)
class PermitAdmin(admin.ModelAdmin):
    list_display = (
        'permit_number',
        'colored_status',
        'colored_priority',
        'permit_type',
        'requester_name',
        'plant',
        'start_date',
        'end_date',
        'overdue_flag',
        'created_at',
    )
    list_filter = (
        'status',
        'priority',
        'permit_type',
        'plant',
        'hazard_risk_level',
        'created_at',
    )
    search_fields = (
        'permit_number',
        'requester_name',
        'contractor_company',
        'supervisor_name',
        'job_description',
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = (
        'permit_number',
        'created_at',
        'updated_at',
        'duration_hours_display',
        'overdue_flag',
    )
    list_per_page = 25
    save_on_top = True

    inlines = [
        PermitContractorInline,
        PermitAttachmentInline,
        PermitApprovalLogInline,
        PermitExtensionInline,
    ]
    fieldsets = (
        ('Identification', {
            'fields': (
                'permit_number',
                ('permit_type', 'status', 'priority'),
                ('duration_hours_display', 'overdue_flag'),
            )
        }),
        ('Requester', {
            'fields': (
                ('requester_user', 'requester_name'),
            )
        }),
        ('Location', {
            'fields': (
                'plant',
                ('zone', 'location'),
                ('sublocation', 'department'),
            )
        }),
        ('Job Details', {
            'fields': ('job_description',)
        }),
        ('Contractor Info', {
            'fields': (
                'contractor_company',
                ('reporting_engineer', 'supervisor_name'),
                'contact_number',
            )
        }),
        ('Schedule', {
            'fields': (('start_date', 'end_date'),)
        }),
        ('Hazard Assessment', {
            'fields': ('hazard_risk_level', 'hazards', 'safety_measures'),
            'classes': ('collapse',),
        }),
        ('Checklist — Equipment & Pipeline', {
            'fields': (
                ('plant_running', 'equipment_isolated', 'valves_closed'),
                ('equipment_drained', 'equipment_disconnected'),
                ('pipeline_depressurized', 'pipeline_drained'),
                ('pipeline_purged', 'pipeline_ventilated'),
                ('electrical_earthing', 'area_protected'),
                ('gas_test', 'gas_test_value'),
                'spillage_removed',
            ),
            'classes': ('collapse',),
        }),
        ('PPE Requirements', {
            'fields': (
                ('ppe_safety_shoe', 'ppe_helmet', 'ppe_safety_belt'),
                ('ppe_gloves', 'ppe_respiratory', 'ppe_ear'),
                ('ppe_eye', 'ppe_other'),
                'ppe_other_specify',
            ),
            'classes': ('collapse',),
        }),
        ('Safety Equipment', {
            'fields': (
                ('electrical_clearance', 'ventilation_adequate'),
                ('fire_extinguishers', 'fire_extinguishers_details'),
                ('grinder_guard', 'welding_elcb'),
                ('gas_cutting_fba', 'gas_hosepipe', 'cylinder_key'),
                'esi_insurance',
            ),
            'classes': ('collapse',),
        }),
        ('Approval', {
            'fields': (
                ('approver', 'rejection_reason'),
                'close_out_notes',
            ),
            'classes': ('collapse',),
        }),
        ('Security Check-in', {
            'fields': (
                ('security_checked_in', 'security_checkin_time'),
                ('employees_count', 'security_esi_insurance'),
                'security_comments',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('collapse',),
        }),
    )
    @admin.display(description='Status', ordering='status')
    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, '#9e9e9e')
        return colored_badge(obj.get_status_display(), color)

    @admin.display(description='Priority', ordering='priority')
    def colored_priority(self, obj):
        color = PRIORITY_COLORS.get(obj.priority, '#9e9e9e')
        return colored_badge(obj.get_priority_display(), color)

    @admin.display(description='Overdue?', boolean=True)
    def overdue_flag(self, obj):
        return obj.is_overdue

    @admin.display(description='Duration (hrs)')
    def duration_hours_display(self, obj):
        return f"{obj.duration_hours} hrs" if obj.duration_hours is not None else '—'
    actions = ['mark_active', 'mark_closed', 'mark_pending']

    @admin.action(description='Mark selected permits as Active')
    def mark_active(self, request, queryset):
        updated = queryset.filter(status='approved').update(status='active')
        self.message_user(request, f"{updated} permit(s) marked as Active.")

    @admin.action(description='Mark selected permits as Closed')
    def mark_closed(self, request, queryset):
        updated = queryset.exclude(status__in=['draft', 'closed']).update(status='closed')
        self.message_user(request, f"{updated} permit(s) marked as Closed.")

    @admin.action(description='Submit selected permits for Approval')
    def mark_pending(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='pending')
        self.message_user(request, f"{updated} permit(s) submitted for approval.")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                'permit_type', 'plant', 'zone', 'location',
                'sublocation', 'department',
                'requester_user', 'approver',
            )
        )


# PERMIT CONTRACTOR
@admin.register(PermitContractor)
class PermitContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'trade', 'id_number', 'esi_number', 'contact_number', 'permit_link')
    search_fields = ('name', 'id_number', 'esi_number', 'permit__permit_number')
    list_filter = ('trade',)
    autocomplete_fields = ('permit',)

    @admin.display(description='Permit')
    def permit_link(self, obj):
        return format_html(
            '<a href="/admin/permits/permit/{}/change/">{}</a>',
            obj.permit_id,
            obj.permit.permit_number or f"#{obj.permit_id}",
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('permit')


# PERMIT APPROVAL LOG
@admin.register(PermitApprovalLog)
class PermitApprovalLogAdmin(admin.ModelAdmin):
    list_display = (
        'permit', 'action', 'from_status', 'to_status',
        'performed_by', 'timestamp',
    )
    list_filter = ('action', 'from_status', 'to_status', 'timestamp')
    search_fields = ('permit__permit_number', 'performed_by__username', 'comments')
    readonly_fields = (
        'permit', 'action', 'from_status', 'to_status',
        'performed_by', 'comments', 'timestamp',
    )
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('permit', 'performed_by')


# PERMIT EXTENSION
@admin.register(PermitExtension)
class PermitExtensionAdmin(admin.ModelAdmin):
    list_display = (
        'permit', 'original_end_date', 'new_end_date',
        'colored_status', 'requested_by', 'reviewed_by', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('permit__permit_number', 'reason', 'requested_by__username')
    readonly_fields = ('original_end_date', 'reviewed_at', 'created_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('permit',)

    fieldsets = (
        ('Extension Request', {
            'fields': (
                'permit',
                ('original_end_date', 'new_end_date'),
                'reason',
                'requested_by',
            )
        }),
        ('Review', {
            'fields': (
                ('status', 'reviewed_by', 'reviewed_at'),
                'review_comments',
            )
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    actions = ['approve_extensions', 'reject_extensions']

    @admin.display(description='Status', ordering='status')
    def colored_status(self, obj):
        colors = {
            'pending':  '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336',
        }
        return colored_badge(obj.get_status_display(), colors.get(obj.status, '#9e9e9e'))

    @admin.action(description='Approve selected extensions')
    def approve_extensions(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} extension(s) approved.")

    @admin.action(description='Reject selected extensions')
    def reject_extensions(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} extension(s) rejected.")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'permit', 'requested_by', 'reviewed_by'
        )


# PERMIT ATTACHMENT
@admin.register(PermitAttachment)
class PermitAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 'permit', 'description',
        'file_size_display', 'uploaded_by', 'uploaded_at',
    )
    search_fields = ('original_filename', 'permit__permit_number', 'description')
    readonly_fields = ('original_filename', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)
    autocomplete_fields = ('permit',)

    @admin.display(description='File Size')
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size >= 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            return f"{obj.file_size / 1024:.1f} KB"
        return '—'

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('permit', 'uploaded_by')