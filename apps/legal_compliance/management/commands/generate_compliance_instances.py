from django.core.management.base import BaseCommand

from apps.legal_compliance.utils import (
    generate_compliance_instances
)


class Command(BaseCommand):

    help = (
        'Generate recurring compliance instances'
    )

    def handle(self, *args, **kwargs):

        generate_compliance_instances()

        self.stdout.write(

            self.style.SUCCESS(

                'Compliance instances generated successfully.'
            )
        )