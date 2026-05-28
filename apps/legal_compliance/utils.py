from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from .models import (ComplianceRequirement,ComplianceFinding,RegulatoryNotice,ComplianceInstance, ComplianceNotification)
from dateutil.relativedelta import relativedelta


# =====================================================
# COMPLIANCE REMINDER ENGINE
# =====================================================

def send_compliance_reminders():

    today = timezone.now().date()

    compliances = (

        ComplianceRequirement.objects

        .filter(
            is_active=True
        )

        .exclude(
            status='COMPLETED'
        )
    )

    for compliance in compliances:

        if not compliance.due_date:

            continue

        days_left = (
            compliance.due_date - today
        ).days

        # ==========================================
        # 15 DAY REMINDER
        # ==========================================

        if days_left == 15:

            for user in compliance.responsible_person.all():

                print(
                    f'15 day reminder sent to {user}'
                )

        # ==========================================
        # 7 DAY REMINDER
        # ==========================================

        elif days_left == 7:

            for user in compliance.responsible_person.all():

                print(
                    f'7 day reminder sent to {user}'
                )

        # ==========================================
        # 1 DAY REMINDER
        # ==========================================

        elif days_left == 1:

            for user in compliance.responsible_person.all():

                print(
                    f'Final reminder sent to {user}'
                )

        # ==========================================
        # OVERDUE ESCALATION
        # ==========================================

        elif days_left < 0:

            compliance.status = 'OVERDUE'

            compliance.save()

            print(
                f'Compliance overdue: '
                f'{compliance.title}'
            )



# =====================================================
# GENERATE COMPLIANCE INSTANCES
# =====================================================

def generate_compliance_instances():

    today = timezone.now().date()

    requirements = (

        ComplianceRequirement.objects

        .filter(
            is_active=True
        )
    )

    for requirement in requirements:

        # ==========================================
        # CHECK EXISTING INSTANCE
        # ==========================================

        existing_instance = (

            ComplianceInstance.objects

            .filter(
                requirement=requirement,
                scheduled_date__month=today.month,
                scheduled_date__year=today.year
            )

            .exists()
        )

        if existing_instance:

            continue

        # ==========================================
        # MONTHLY
        # ==========================================

        if requirement.frequency == 'MONTHLY':

            due_date = (
                today + relativedelta(months=1)
            )

        # ==========================================
        # QUARTERLY
        # ==========================================

        elif requirement.frequency == 'QUARTERLY':

            due_date = (
                today + relativedelta(months=3)
            )

        # ==========================================
        # HALF YEARLY
        # ==========================================

        elif requirement.frequency == 'HALF_YEARLY':

            due_date = (
                today + relativedelta(months=6)
            )

        # ==========================================
        # YEARLY
        # ==========================================

        elif requirement.frequency == 'YEARLY':

            due_date = (
                today + relativedelta(years=1)
            )

        else:

            due_date = today + timedelta(days=30)

        # ==========================================
        # CREATE INSTANCE
        # ==========================================

        ComplianceInstance.objects.create(

            requirement=requirement,

            scheduled_date=today,

            due_date=due_date,

            status='PENDING'
        )

        print(
            f'Created instance for '
            f'{requirement.title}'
        )




# =====================================================
# CREATE NOTIFICATION
# =====================================================

def create_notification(

    user,

    notification_type,

    title,

    message,

    redirect_url=None
):

    ComplianceNotification.objects.create(

        user=user,

        notification_type=notification_type,

        title=title,

        message=message,

        redirect_url=redirect_url
    )