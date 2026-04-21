from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from apps.organizations.models import Location, Plant, Zone, SubLocation


class AuditCategory(models.Model):
    category_name = models.CharField(max_length=200, unique=True)
    category_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_audit_categories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category_name"]
        verbose_name = "Audit Category"
        verbose_name_plural = "Audit Categories"

    def __str__(self):
        return f"{self.category_code} - {self.category_name}"


class AuditTemplate(models.Model):

    title = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    category = models.ForeignKey(
        AuditCategory,
        on_delete=models.PROTECT,
        related_name="templates",
    )
    standard_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "version"]
        unique_together = ["title", "version"]

    def __str__(self):
        return f"{self.title} v{self.version}"


class AuditQuestion(models.Model):
    template = models.ForeignKey(
        AuditTemplate,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.TextField()
    compliance_clause = models.CharField(max_length=255, blank=True)
    is_mandatory_photo = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["template", "sequence", "id"]

    def __str__(self):
        return f"{self.template.title} - Q{self.sequence}"


class AuditSchedule(models.Model):
    PRIORITY_CRITICAL = "CRITICAL"
    PRIORITY_HIGH = "HIGH"
    PRIORITY_MEDIUM = "MEDIUM"
    PRIORITY_LOW = "LOW"

    STATUS_DRAFT = "DRAFT"
    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CLOSED = "CLOSED"

    PRIORITY_CHOICES = [
        (PRIORITY_CRITICAL, "Critical"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_LOW, "Low"),
    ]

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_IN_PROGRESS, "In-Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CLOSED, "Closed"),
    ]

    schedule_code = models.CharField(max_length=100, unique=True, editable=False)
    template = models.ForeignKey(
        AuditTemplate,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    auditor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_schedules",
    )
    plants = models.ManyToManyField(
        Plant,
        blank=True,
        related_name="audit_schedules",
    )
    zones = models.ManyToManyField(
        Zone,
        blank=True,
        related_name="audit_schedules",
    )
    locations = models.ManyToManyField(
        Location,
        blank=True,
        related_name="audit_schedules_multi",
    )
    sublocations = models.ManyToManyField(
        SubLocation,
        blank=True,
        related_name="audit_schedules",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="audit_schedules",
        null=True,
        blank=True,
    )
    scheduled_date = models.DateField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-created_at"]

    def __str__(self):
        return self.schedule_code

    def save(self, *args, **kwargs):
        if not self.schedule_code:
            self.schedule_code = self.generate_schedule_code()
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.status in [self.STATUS_COMPLETED, self.STATUS_CLOSED]:
            missing_photo_failures = self.responses.filter(
                status=AuditResponse.STATUS_FAIL,
                question__is_mandatory_photo=True,
            ).filter(models.Q(photo_evidence="") | models.Q(photo_evidence__isnull=True))
            if missing_photo_failures.exists():
                raise ValidationError(
                    {
                        "status": (
                            "This audit cannot be completed while failed responses with "
                            "mandatory photo evidence are still missing photos."
                        )
                    }
                )

        if self.status == self.STATUS_CLOSED:
            unresolved_findings = self.findings.filter(
                is_archived=False
            ).exclude(
                status__in=[AuditFinding.STATUS_RESOLVED, AuditFinding.STATUS_CLOSED]
            )
            if unresolved_findings.exists():
                raise ValidationError(
                    {
                        "status": (
                            "This audit cannot be closed until every finding is "
                            "Resolved or Closed."
                        )
                    }
                )

    def generate_schedule_code(self):
        prefix = timezone.now().strftime("AUD-%Y%m")
        last_schedule = (
            AuditSchedule.objects.filter(schedule_code__startswith=prefix)
            .order_by("-schedule_code")
            .first()
        )
        if last_schedule:
            try:
                next_number = int(last_schedule.schedule_code.split("-")[-1]) + 1
            except (TypeError, ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        return f"{prefix}-{next_number:04d}"

    @property
    def primary_location(self):
        return self.locations.first() or self.location

    @property
    def location_scope(self):
        locations = list(self.locations.values_list("name", flat=True)[:3])
        if locations:
            extra = self.locations.count() - len(locations)
            suffix = f" +{extra} more" if extra > 0 else ""
            return ", ".join(locations) + suffix
        if self.location:
            return self.location.name
        return "-"


class AuditResponse(models.Model):
    STATUS_PASS = "PASS"
    STATUS_FAIL = "FAIL"
    STATUS_NA = "NA"

    STATUS_CHOICES = [
        (STATUS_PASS, "Pass"),
        (STATUS_FAIL, "Fail"),
        (STATUS_NA, "N/A"),
    ]

    schedule = models.ForeignKey(
        AuditSchedule,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    question = models.ForeignKey(
        AuditQuestion,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True)
    photo_evidence = models.ImageField(
        upload_to="audit/responses/",
        blank=True,
        null=True,
    )
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["question__sequence", "id"]
        unique_together = ["schedule", "question"]

    def __str__(self):
        return f"{self.schedule.schedule_code} - Q{self.question.sequence}"


class AuditFinding(models.Model):
    RISK_CRITICAL = "CRITICAL"
    RISK_MAJOR = "MAJOR"
    RISK_MINOR = "MINOR"

    STATUS_DRAFT = "DRAFT"
    STATUS_OPEN = "OPEN"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_RESOLVED = "RESOLVED"
    STATUS_CLOSED = "CLOSED"

    REVIEW_PENDING = "PENDING"
    REVIEW_APPROVED = "APPROVED"
    REVIEW_REJECTED = "REJECTED"

    RISK_CHOICES = [
        (RISK_CRITICAL, "Critical"),
        (RISK_MAJOR, "Major"),
        (RISK_MINOR, "Minor"),
    ]
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In-Progress"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_CLOSED, "Closed"),
    ]
    REVIEW_CHOICES = [
        (REVIEW_PENDING, "Pending"),
        (REVIEW_APPROVED, "Approved"),
        (REVIEW_REJECTED, "Rejected"),
    ]

    finding_id = models.CharField(max_length=30, unique=True, editable=False)
    parent_audit = models.ForeignKey(
        AuditSchedule,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    origin_question = models.ForeignKey(
        AuditQuestion,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    observation_detail = models.TextField()
    risk_score = models.CharField(
        max_length=20,
        choices=RISK_CHOICES,
        default=RISK_MAJOR,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    manager_review_status = models.CharField(
        max_length=20,
        choices=REVIEW_CHOICES,
        default=REVIEW_PENDING,
    )
    manager_review_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_audit_findings",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent_audit", "origin_question"],
                name="unique_finding_per_audit_question",
            )
        ]

    def __str__(self):
        return self.finding_id

    def save(self, *args, **kwargs):
        if not self.finding_id:
            self.finding_id = self.generate_finding_id()
        super().save(*args, **kwargs)

    def generate_finding_id(self):
        year = timezone.now().year
        prefix = f"NC-{year}"
        last_finding = (
            AuditFinding.objects.filter(finding_id__startswith=prefix)
            .order_by("-finding_id")
            .first()
        )
        if last_finding:
            try:
                next_number = int(last_finding.finding_id.split("-")[-1]) + 1
            except (TypeError, ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        return f"{prefix}-{next_number:03d}"

    def archive(self, reason=""):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.manager_review_comment = reason or self.manager_review_comment
        if self.status not in [self.STATUS_RESOLVED, self.STATUS_CLOSED]:
            self.status = self.STATUS_CLOSED
        self.save(
            update_fields=[
                "is_archived",
                "archived_at",
                "manager_review_comment",
                "status",
                "updated_at",
            ]
        )


class CAPA(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_FIXED = "FIXED"
    STATUS_VERIFIED = "VERIFIED"

    VERIFICATION_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_FIXED, "Fixed"),
        (STATUS_VERIFIED, "Verified"),
    ]

    finding = models.ForeignKey(
        AuditFinding,
        on_delete=models.CASCADE,
        related_name="capas",
    )
    action_required = models.TextField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_capas",
    )
    due_date = models.DateField()
    evidence_of_fix = models.ImageField(
        upload_to="audit/capa/",
        blank=True,
        null=True,
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=STATUS_PENDING,
    )
    fixed_comment = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_capas",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return f"CAPA - {self.finding.finding_id}"
