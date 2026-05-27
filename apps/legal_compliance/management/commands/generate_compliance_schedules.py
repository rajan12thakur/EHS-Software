from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.legal_compliance.models import (
    ComplianceRequirement,
    ComplianceSchedule
)


class Command(BaseCommand):

    help = 'Generate recurring compliance schedules'


    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        requirements = (
            ComplianceRequirement.objects.filter(
                is_active=True,
                next_due_date__isnull=False
            )
        )

        created_count = 0

        for requirement in requirements:

            due_date = requirement.next_due_date

            # CHECK EXISTING SCHEDULE

            schedule_exists = (
                ComplianceSchedule.objects.filter(
                    compliance_requirement=requirement,
                    due_date=due_date
                ).exists()
            )

            if schedule_exists:
                continue

            # CREATE SCHEDULE

            ComplianceSchedule.objects.create(

                compliance_requirement=requirement,

                due_date=due_date,

                assigned_to=requirement.responsible_person,

                status='PENDING'
            )

            created_count += 1

            # UPDATE NEXT DUE DATE

            if requirement.frequency == 'DAILY':

                requirement.next_due_date = (
                    due_date + timedelta(days=1)
                )

            elif requirement.frequency == 'WEEKLY':

                requirement.next_due_date = (
                    due_date + timedelta(days=7)
                )

            elif requirement.frequency == 'MONTHLY':

                requirement.next_due_date = (
                    due_date + timedelta(days=30)
                )

            elif requirement.frequency == 'QUARTERLY':

                requirement.next_due_date = (
                    due_date + timedelta(days=90)
                )

            elif requirement.frequency == 'HALF_YEARLY':

                requirement.next_due_date = (
                    due_date + timedelta(days=180)
                )

            elif requirement.frequency == 'YEARLY':

                requirement.next_due_date = (
                    due_date + timedelta(days=365)
                )

            requirement.save()

        self.stdout.write(

            self.style.SUCCESS(

                f'{created_count} compliance schedules generated successfully.'
            )
        )