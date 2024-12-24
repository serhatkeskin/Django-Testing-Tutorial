from django.core.management.base import BaseCommand
from myapp.models import MyModel
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'This command will create 10 MyModel objects'

    def handle(self, *args, **options):
        for i in range(10):
            MyModel.objects.create(
                name=f'Object {i}',
                description=f'This is object {i}',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Successfully created 10 MyModel objects'))

