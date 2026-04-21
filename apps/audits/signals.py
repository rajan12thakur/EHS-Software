from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditFinding, AuditResponse


@receiver(post_save, sender=AuditResponse)
def create_finding_for_failed_response(sender, instance, created, **kwargs):
    if instance.status != AuditResponse.STATUS_FAIL:
        return

    finding_defaults = {
        "observation_detail": instance.comment or instance.question.question_text,
        "risk_score": AuditFinding.RISK_MAJOR,
        "status": AuditFinding.STATUS_DRAFT,
        "manager_review_status": AuditFinding.REVIEW_PENDING,
        "is_archived": False,
    }

    finding, was_created = AuditFinding.objects.get_or_create(
        parent_audit=instance.schedule,
        origin_question=instance.question,
        defaults=finding_defaults,
    )

    if not was_created and finding.is_archived:
        finding.is_archived = False
        finding.archived_at = None
        finding.status = AuditFinding.STATUS_DRAFT
        finding.manager_review_status = AuditFinding.REVIEW_PENDING
        if instance.comment:
            finding.observation_detail = instance.comment
        finding.save(
            update_fields=[
                "is_archived",
                "archived_at",
                "status",
                "manager_review_status",
                "observation_detail",
                "updated_at",
            ]
        )
