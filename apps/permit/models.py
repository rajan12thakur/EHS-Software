from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.organizations.models import Plant, Zone, Location, SubLocation, Department
import os


# HELPERS
def yes_no_na_field(**kwargs):
    """Reusable factory for Yes/No/N/A choice fields."""
    return models.CharField(
        max_length=10,
        choices=[('yes', 'Yes'), ('no', 'No'), ('na', 'N/A')],
        blank=True,
        null=True,
        **kwargs
    )


def validate_attachment(value):
    """Validate file type and size for permit attachments"""

    if not value:
        return
    try:
        if not value.name:
            return

        if hasattr(value, 'path') and not os.path.exists(value.path):
            return
    except Exception:
        return
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_extensions)}"
        )

    # Size validation
    max_size_mb = 10
    try:
        if value.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size cannot exceed {max_size_mb}MB.")
    except Exception:
        pass

def permit_attachment_path(instance, filename):
    permit_id = instance.permit.id if instance.permit_id else "temp"
    return f'permit_attachments/permit_{permit_id}/{filename}'


def permit_closure_photo_path(instance, filename):
    permit_id = instance.closure.permit_id if instance.closure_id else "temp"
    return f'permit_closures/permit_{permit_id}/{filename}'


# PERMIT TYPE
class PermitType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permit_types_created'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Permit Type'
        verbose_name_plural = 'Permit Types'

    def __str__(self):
        return f"{self.name} ({self.code})"


# PERMIT
class Permit(models.Model):
    # CHOICES
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('reapproval', 'Pending Re-approval'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]

    HAZARD_RISK_LEVEL_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    permit_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated on first save. Format: PTW-YYYY-NNNNN"
    )
    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permits'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )

    requester_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_permits'
    )
    requester_name = models.CharField(max_length=255)
    plant = models.ForeignKey(
        Plant, on_delete=models.SET_NULL, null=True, related_name='permits'
    )
    zone = models.ForeignKey(
        Zone, on_delete=models.SET_NULL, null=True, related_name='permits'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name='permits'
    )
    sublocation = models.ForeignKey(
        SubLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='permits'
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='permits'
    )
    job_description = models.TextField()
    contractor_company = models.CharField(max_length=255, blank=True, null=True)
    reporting_engineer = models.CharField(max_length=255, blank=True, null=True)
    supervisor_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )
    hazard_risk_level = models.CharField(
        max_length=20,
        choices=HAZARD_RISK_LEVEL_CHOICES,
        blank=True,
        null=True
    )
    hazards = models.JSONField(default=list, blank=True)
    safety_measures = models.TextField(blank=True, null=True)

    #check list fields
    plant_running = yes_no_na_field()
    equipment_isolated = yes_no_na_field()
    valves_closed = yes_no_na_field()
    equipment_drained = yes_no_na_field()
    equipment_disconnected = yes_no_na_field()
    pipeline_depressurized = yes_no_na_field()
    pipeline_drained = yes_no_na_field()
    pipeline_purged = yes_no_na_field()
    pipeline_ventilated = yes_no_na_field()
    electrical_earthing = yes_no_na_field()
    area_protected = yes_no_na_field()
    gas_test = yes_no_na_field()
    gas_test_value = models.FloatField(
        blank=True,
        null=True,
        help_text="Gas test reading (e.g. LEL %)"
    )
    spillage_removed = yes_no_na_field()

    # PPE
    ppe_safety_shoe = yes_no_na_field()
    ppe_helmet = yes_no_na_field()
    ppe_safety_belt = yes_no_na_field()
    ppe_gloves = yes_no_na_field()
    ppe_respiratory = yes_no_na_field()
    ppe_ear = yes_no_na_field()
    ppe_eye = yes_no_na_field()
    ppe_other = yes_no_na_field()
    ppe_other_specify = models.CharField(max_length=255, blank=True, null=True)

    # SAFETY EQUIPMENT
    electrical_clearance = yes_no_na_field()
    ventilation_adequate = yes_no_na_field()
    fire_extinguishers = yes_no_na_field()
    fire_extinguishers_details = models.CharField(max_length=255, blank=True, null=True)

    grinder_guard = yes_no_na_field()
    welding_elcb = yes_no_na_field()

    gas_cutting_fba = yes_no_na_field()
    gas_hosepipe = yes_no_na_field()
    cylinder_key = yes_no_na_field()

    esi_insurance = yes_no_na_field()

    # APPROVAL
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_permits'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    close_out_notes = models.TextField(blank=True, null=True)

    # SECURITY CHECK-IN
    security_checked_in = models.BooleanField(default=False)
    security_checkin_time = models.DateTimeField(null=True, blank=True)
    security_comments = models.TextField(blank=True, null=True)
    security_esi_insurance = models.CharField(max_length=255, blank=True, null=True)
    employees_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of employees checked in by security"
    )

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Permit'
        verbose_name_plural = 'Permits'
        indexes = [
            models.Index(fields=['status', 'plant']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['requester_user', 'status']),
            models.Index(fields=['priority', 'status']),
        ]

    def clean(self):
        errors = {}

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['end_date'] = "End date cannot be before start date."

        if self.zone and self.plant and self.zone.plant != self.plant:
            errors['zone'] = "Zone does not belong to the selected Plant."

        if self.location and self.zone and self.location.zone != self.zone:
            errors['location'] = "Location does not belong to the selected Zone."

        if self.sublocation and self.location and self.sublocation.location != self.location:
            errors['sublocation'] = "SubLocation does not belong to the selected Location."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.requester_user and not self.requester_name:
            self.requester_name = (
                self.requester_user.get_full_name()
                or self.requester_user.username
            )

        super().save(*args, **kwargs)
        if not self.permit_number:
            year = self.created_at.year
            self.permit_number = f"PTW-{year}-{self.id:05d}"
            Permit.objects.filter(pk=self.pk).update(permit_number=self.permit_number)

    def __str__(self):
        ref = self.permit_number or f"#{self.id}"
        type_name = self.permit_type.name if self.permit_type else 'N/A'
        return f"Permit {ref} — {type_name}"

    @property
    def is_overdue(self):
        """True if the permit is still active/approved but past its end date."""
        from django.utils import timezone
        return (
            self.status in ('approved', 'active')
            and self.end_date
            and timezone.now() > self.end_date
        )

    @property
    def duration_hours(self):
        """Total permitted work duration in hours."""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return round(delta.total_seconds() / 3600, 2)
        return None


# PERMIT CONTRACTOR 
class PermitContractor(models.Model):
    """Individual worker / contractor associated with a permit."""

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name='contractors'
    )
    name = models.CharField(max_length=255)
    trade = models.CharField(max_length=100, blank=True, null=True)
    id_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Government ID / Employee ID"
    )
    esi_number = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Permit Contractor'
        verbose_name_plural = 'Permit Contractors'

    def __str__(self):
        return f"{self.name} — Permit {self.permit_id}"


# PERMIT APPROVAL LOG
class PermitApprovalLog(models.Model):
    """
    Immutable audit trail of every status change on a permit.
    Create a new log entry on every approval, rejection, or re-submission.
    """

    ACTION_CHOICES = [
        ('created', 'Created'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resubmitted', 'Re-submitted'),
        ('activated', 'Activated'),
        ('closed', 'Closed'),
        ('extended', 'Extended'),
        ('cancelled', 'Cancelled'),
    ]

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name='approval_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permit_actions'
    )
    comments = models.TextField(blank=True)

    from_status = models.CharField(max_length=20, blank=True, null=True)
    to_status = models.CharField(max_length=20, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Permit Approval Log'
        verbose_name_plural = 'Permit Approval Logs'

    def __str__(self):
        return (
            f"Permit #{self.permit_id} — {self.get_action_display()} "
            f"by {self.performed_by} at {self.timestamp:%Y-%m-%d %H:%M}"
        )


# PERMIT EXTENSION REQUEST
class PermitExtension(models.Model):
    """
    Tracks requests to extend a permit's end_date.
    Each extension must be re-approved.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name='extensions'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permit_extensions_requested'
    )
    original_end_date = models.DateTimeField()
    new_end_date = models.DateTimeField()
    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permit_extensions_reviewed'
    )
    review_comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Permit Extension'
        verbose_name_plural = 'Permit Extensions'

    def clean(self):
        if self.new_end_date and self.original_end_date:
            if self.new_end_date <= self.original_end_date:
                raise ValidationError({
                    'new_end_date': "New end date must be after the original end date."
                })

    def __str__(self):
        return f"Extension for Permit #{self.permit_id} → {self.new_end_date:%Y-%m-%d}"


class PermitClosure(models.Model):
    WORK_STATUS_CHOICES = [
        ('completed', 'Completed Successfully'),
        ('completed_with_issues', 'Completed with Minor Issues'),
        ('partially_completed', 'Partially Completed'),
        ('not_completed', 'Not Completed'),
    ]

    permit = models.OneToOneField(
        Permit,
        on_delete=models.CASCADE,
        related_name='closure'
    )
    actual_end_date = models.DateTimeField()
    work_status = models.CharField(max_length=30, choices=WORK_STATUS_CHOICES)
    work_summary = models.TextField()
    issues_encountered = models.TextField(blank=True)
    area_inspected = models.BooleanField(default=False)
    fire_watch_completed = models.BooleanField(default=False)
    equipment_isolated = models.BooleanField(default=False)
    hazards_removed = models.BooleanField(default=False)
    barriers_removed = models.BooleanField(default=False)
    no_incidents = models.BooleanField(default=False)
    area_clean = models.BooleanField(default=False)
    systems_operational = models.BooleanField(default=False)
    contractor_signature = models.TextField()
    safety_signature = models.TextField()
    closure_comments = models.TextField(blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='closed_permits'
    )
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-closed_at']
        verbose_name = 'Permit Closure'
        verbose_name_plural = 'Permit Closures'

    def clean(self):
        errors = {}
        if self.actual_end_date and self.permit_id:
            if self.permit.start_date and self.actual_end_date < self.permit.start_date:
                errors['actual_end_date'] = "Actual completion cannot be before the permit start date."
            from django.utils import timezone
            if self.actual_end_date > timezone.now():
                errors['actual_end_date'] = "Actual completion cannot be in the future."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Closure for {self.permit}"


class PermitClosurePhoto(models.Model):
    closure = models.ForeignKey(
        PermitClosure,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo = models.ImageField(upload_to=permit_closure_photo_path)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permit_closure_photos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Permit Closure Photo'
        verbose_name_plural = 'Permit Closure Photos'

    def __str__(self):
        return f"Closure photo for Permit #{self.closure.permit_id}"


# PERMIT ATTACHMENT
class PermitAttachment(models.Model):
    permit = models.ForeignKey(
        Permit,
        related_name='attachments',
        on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to=permit_attachment_path,
        validators=[validate_attachment]
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original name of the uploaded file"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    description = models.CharField(max_length=255, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Permit Attachment'
        verbose_name_plural = 'Permit Attachments'

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_filename or os.path.basename(self.file.name)
