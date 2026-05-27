from django.core.management.base import BaseCommand

from django.utils import timezone

from apps.legal_compliance.models import (
    ComplianceSchedule
)


class Command(BaseCommand):

    help = 'Check and update overdue compliance schedules'


    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        overdue_schedules = (
            ComplianceSchedule.objects.filter(
                due_date__lt=today
            )
            .exclude(
                status__in=[
                    'APPROVED',
                    'SUBMITTED'
                ]
            )
        )

        updated_count = 0

        for schedule in overdue_schedules:

            if schedule.status != 'OVERDUE':

                schedule.status = 'OVERDUE'

                schedule.save()

                updated_count += 1

        self.stdout.write(

            self.style.SUCCESS(

                f'{updated_count} schedules marked as overdue.'
            )
        )