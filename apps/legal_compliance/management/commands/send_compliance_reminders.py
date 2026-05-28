from django.core.management.base import BaseCommand

from apps.legal_compliance.utils import (
    send_compliance_reminders
)


class Command(BaseCommand):

    help = (
        'Send compliance reminders'
    )

    def handle(self, *args, **kwargs):

        send_compliance_reminders()

        self.stdout.write(

            self.style.SUCCESS(

                'Compliance reminders processed successfully.'
            )
        )