from django.core.management.base import BaseCommand
from myapp.models import MyModel
from django.utils import timezone
import time
from faker import Faker


class Command(BaseCommand):
    help = 'This command will create a MyModel object with fake data using Faker'

    def handle(self, *args, **options):
        # Initialize Faker
        faker = Faker()

        # Generate a fake MyModel instance
        fake_instance = MyModel(
            name=faker.name(),
            description=faker.text(),
            created_at=faker.date_time(),
            updated_at=faker.date_time()
        )

        # Save the instance to the database
        fake_instance.save()

        # Output for verification
        print("### fake_instance.name:",fake_instance.name,
              "fake_instance.description:", fake_instance.description)


