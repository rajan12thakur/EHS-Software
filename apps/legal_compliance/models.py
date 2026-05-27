from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.organizations.models import Plant, Department

class LegalAct(models.Model):
    """
    Master Regulatory Registry
    Examples:
    - Factories Act
    - Hazardous Waste Rules
    - Fire NOC
    """

    GOVERNMENT_LEVEL_CHOICES = [
        ('CENTRAL', 'Central'),
        ('STATE', 'State'),
        ('LOCAL', 'Local'),
        ('INTERNATIONAL', 'International'),
        ('INTERNAL', 'Internal'),
    ]

    CATEGORY_CHOICES = [
        ('SAFETY', 'Safety'),
        ('ENVIRONMENT', 'Environment'),
        ('HEALTH', 'Health'),
        ('LABOUR', 'Labour'),
        ('FIRE', 'Fire'),
        ('ELECTRICAL', 'Electrical'),
        ('CHEMICAL', 'Chemical'),
        ('FACTORY', 'Factory'),
        ('ESG', 'ESG'),
        ('ISO', 'ISO'),
        ('OTHER', 'Other'),
    ]

    act_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    act_name = models.CharField(
        max_length=255
    )

    short_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    authority_name = models.CharField(
        max_length=255,
        help_text="Example: Pollution Control Board, Factory Inspector"
    )

    government_level = models.CharField(
        max_length=20,
        choices=GOVERNMENT_LEVEL_CHOICES
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    applicability_notes = models.TextField(
        blank=True,
        null=True
    )

    effective_date = models.DateField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='legal_acts_created'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['act_name']
        verbose_name = 'Legal Act'
        verbose_name_plural = 'Legal Acts'

    def __str__(self):
        return f"{self.act_code} - {self.act_name}"

    def save(self, *args, **kwargs):
        if not self.act_code:
            year = timezone.now().year

            last_act = LegalAct.objects.filter(
                act_code__startswith=f'ACT-{year}'
            ).order_by('-id').first()

            if last_act:
                try:
                    last_number = int(last_act.act_code.split('-')[-1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1

            self.act_code = f'ACT-{year}-{new_number:03d}'

        super().save(*args, **kwargs)


class ComplianceQuestion(models.Model):
    """
    Master Compliance Questions linked with Legal Acts.
    """

    QUESTION_TYPE_CHOICES = [

        ('YES_NO', 'Yes / No'),

        ('TEXT', 'Text Input'),

        ('NUMBER', 'Numeric Input'),

        ('DATE', 'Date'),
    ]


    SUBMISSION_TYPE_CHOICES = [

        ('DOCUMENT', 'Document Upload'),

        ('CHECKLIST', 'Checklist'),

        ('BOTH', 'Checklist + Document'),

        ('AUTO', 'Auto Compliance'),
    ]


    question_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    legal_act = models.ForeignKey(
        LegalAct,
        on_delete=models.CASCADE,
        related_name='compliance_questions'
    )

    question_text = models.TextField(
        verbose_name='Question'
    )

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='YES_NO'
    )

    submission_type = models.CharField(
        max_length=20,
        choices=SUBMISSION_TYPE_CHOICES,
        default='CHECKLIST'
    )

    # CONFIGURATION

    is_mandatory = models.BooleanField(
        default=True
    )

    is_document_required = models.BooleanField(
        default=False
    )

    is_critical = models.BooleanField(
        default=False
    )

    auto_generate_finding = models.BooleanField(
        default=True,
        help_text='Auto-create finding for non-compliance'
    )

    # REFERENCE

    reference_standard = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Example: OSHA 1910, Factory Act Section'
    )

    guidance_notes = models.TextField(
        blank=True,
        null=True
    )

    # APPLICABILITY

    applicable_plants = models.ManyToManyField(
        Plant,
        blank=True,
        related_name='compliance_questions'
    )

    applicable_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='department_compliance_questions'
    )

    # STATUS

    is_active = models.BooleanField(
        default=True
    )

    # AUDIT

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_compliance_questions'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_compliance_questions'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            'legal_act',
            'question_code'
        ]

        verbose_name = 'Compliance Question'

        verbose_name_plural = 'Compliance Questions'

        indexes = [

            models.Index(
                fields=[
                    'legal_act',
                    'submission_type',
                    'is_active'
                ]
            ),

            models.Index(
                fields=[
                    'question_code'
                ]
            ),
        ]

    def __str__(self):

        return (
            f"{self.question_code} - "
            f"{self.question_text[:50]}"
        )

    def save(self, *args, **kwargs):

        if not self.question_code:

            act_code = (
                self.legal_act.act_code
                if self.legal_act else 'GEN'
            )

            prefix = (
                act_code.replace('ACT-', 'CQ-')
            )

            last_question = (
                ComplianceQuestion.objects.filter(
                    question_code__startswith=prefix
                )
                .order_by('-id')
                .first()
            )

            if last_question:

                try:

                    last_number = int(
                        last_question.question_code.split('-')[-1]
                    )

                    new_number = last_number + 1

                except:

                    new_number = 1

            else:

                new_number = 1

            self.question_code = (
                f"{prefix}-{new_number:03d}"
            )

        super().save(*args, **kwargs)

class ComplianceRequirement(models.Model):
    """
    Operational Compliance Obligation
    Examples:
    - Submit Annual Return
    - Renew Factory License
    - Conduct Medical Examination
    """

    FREQUENCY_CHOICES = [
        ('ONE_TIME', 'One Time'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('YEARLY', 'Yearly'),
        ('EVENT_BASED', 'Event Based'),
    ]

    CRITICALITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('OVERDUE', 'Overdue'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    requirement_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    title = models.CharField(
        max_length=255
    )

    legal_act = models.ForeignKey(
        LegalAct,
        on_delete=models.CASCADE,
        related_name='requirements'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    frequency = models.CharField(
        max_length=30,
        choices=FREQUENCY_CHOICES
    )

    criticality = models.CharField(
        max_length=20,
        choices=CRITICALITY_CHOICES,
        default='MEDIUM'
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    evidence_required = models.BooleanField(
        default=True
    )

    requires_approval = models.BooleanField(
        default=True
    )

    due_days_before = models.PositiveIntegerField(
        default=7,
        help_text="Create compliance task before due date"
    )

    next_due_date = models.DateField(
        null=True,
        blank=True
    )

    reminder_days = models.PositiveIntegerField(
        default=3,
        help_text="Reminder before due date"
    )

    escalation_days = models.PositiveIntegerField(
        default=1,
        help_text="Escalate after overdue days"
    )

    applicable_plants = models.ManyToManyField(
        Plant,
        blank=True,
        related_name='compliance_requirements'
    )

    applicable_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='compliance_requirements'
    )

    responsible_person = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='compliance_responsibilities'
    )


    reviewer = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='compliance_reviews'
    )

    questions = models.ManyToManyField(
        ComplianceQuestion,
        through='ComplianceRequirementQuestion',
        blank=True,
        related_name='requirements'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_requirements_created'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Compliance Requirement'
        verbose_name_plural = 'Compliance Requirements'

    def __str__(self):
        return f"{self.requirement_code} - {self.title}"

    def save(self, *args, **kwargs):

        if not self.requirement_code:

            year = timezone.now().year

            last_requirement = ComplianceRequirement.objects.filter(
                requirement_code__startswith=f'REQ-{year}'
            ).order_by('-id').first()

            if last_requirement:

                try:

                    last_number = int(
                        last_requirement.requirement_code.split('-')[-1]
                    )

                    new_number = last_number + 1

                except:

                    new_number = 1

            else:

                new_number = 1

            self.requirement_code = (
                f'REQ-{year}-{new_number:03d}'
            )

        # ======================================
        # AUTO STATUS UPDATE
        # ======================================

        # ======================================
        # AUTO OVERDUE LOGIC
        # ======================================

        if (self.due_date and timezone.now().date() > self.due_date and
            self.status not in ['SUBMITTED','COMPLETED']
        ):
            self.status = 'OVERDUE'

        super().save(*args, **kwargs)


class ComplianceRequirementQuestion(models.Model):
    """
    Maps Compliance Questions to Compliance Requirements
    """

    compliance_requirement = models.ForeignKey(

        ComplianceRequirement,

        on_delete=models.CASCADE,

        related_name='requirement_questions'
    )

    question = models.ForeignKey(

        ComplianceQuestion,

        on_delete=models.CASCADE,

        related_name='requirement_mappings'
    )

    is_mandatory = models.BooleanField(
        default=True
    )

    section_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Group questions into sections'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = 'compliance_requirement_questions'

        unique_together = [
            'compliance_requirement',
            'question'
        ]

        ordering = [
            'id'
        ]

        verbose_name = 'Compliance Requirement Question'

        verbose_name_plural = (
            'Compliance Requirement Questions'
        )

    def __str__(self):

        return (

            f"{self.compliance_requirement.title} - "

            f"{self.question.question_code}"
        )
  
class ComplianceSubmission(models.Model):
    """
    Stores completed compliance submissions.
    """

    STATUS_CHOICES = [

        ('DRAFT', 'Draft'),

        ('SUBMITTED', 'Submitted'),

        ('APPROVED', 'Approved'),

        ('REJECTED', 'Rejected'),
    ]

    requirement = models.ForeignKey(

        ComplianceRequirement,

        on_delete=models.CASCADE,

        related_name='submissions'
    )

    submitted_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name='compliance_submissions'
    )

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='DRAFT'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    reviewer_comments = models.TextField(
        blank=True,
        null=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_compliance_submissions'
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        db_table = 'compliance_submissions'

        ordering = ['-created_at']

    def __str__(self):

        return (
            f"{self.requirement.title} - "
            f"{self.status}"
        )
    

class ComplianceResponse(models.Model):
    """
    Stores answers for each compliance question.
    """

    ANSWER_CHOICES = [

        ('YES', 'Yes'),

        ('NO', 'No'),

        ('NA', 'Not Applicable'),
    ]

    submission = models.ForeignKey(

        ComplianceSubmission,

        on_delete=models.CASCADE,

        related_name='responses'
    )

    question = models.ForeignKey(

        ComplianceQuestion,

        on_delete=models.CASCADE
    )

    answer = models.CharField(

        max_length=10,

        choices=ANSWER_CHOICES,

        blank=True,
        null=True
    )

    text_answer = models.TextField(
        blank=True,
        null=True
    )

    number_answer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    date_answer = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    evidence_file = models.FileField(
        upload_to='compliance_responses/',
        blank=True,
        null=True
    )

    is_non_compliant = models.BooleanField(
        default=False
    )

    answered_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = 'compliance_responses'

        unique_together = [
            'submission',
            'question'
        ]

    def __str__(self):

        return (
            f"{self.question.question_code}"
        )

    def save(self, *args, **kwargs):

        # AUTO NON-COMPLIANCE DETECTION

        if self.answer == 'NO':

            self.is_non_compliant = True

        super().save(*args, **kwargs)



# =====================================================
# COMPLIANCE FINDINGS / CAPA
# =====================================================

class ComplianceFinding(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
    ]
    finding_reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )
    requirement = models.ForeignKey(
        ComplianceRequirement,
        on_delete=models.CASCADE,
        related_name='findings'
    )
    submission = models.ForeignKey(
        ComplianceSubmission,
        on_delete=models.CASCADE,
        related_name='findings',
        null=True,
        blank=True
    )
    finding_description = models.TextField()
    violated_provision = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    corrective_action = models.TextField(
        blank=True,
        null=True
    )

    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_assigned_findings'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_review_findings'
    )
    target_date = models.DateField(
        null=True,
        blank=True
    )
    closure_date = models.DateField(
        null=True,
        blank=True
    )
    evidence_file = models.FileField(
        upload_to='compliance_findings/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    remarks = models.TextField(
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_findings'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:
        db_table = 'compliance_findings'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.finding_reference:
            last_id = (
                ComplianceFinding.objects.count() + 1
            )
            self.finding_reference = (
                f'FND-{timezone.now().year}-{last_id:03d}'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.finding_reference