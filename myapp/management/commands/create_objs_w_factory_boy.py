from django.core.management.base import BaseCommand
from myapp.models import MyModel
from django.utils import timezone
import time
import factory


class Command(BaseCommand):
    help = 'This command will create a MyModel object with fake data using Factory Boy'

    def handle(self, *args, **options):
        class MyModelFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = MyModel  # Link the factory to the MyModel class

            name = factory.Faker('name')  # Generate fake name
            description = factory.Faker('text')  # Generate fake text
            created_at = factory.Faker('date_time')  # Generate fake datetime
            updated_at = factory.Faker('date_time')  # Generate fake datetime

        # Create an instance (not saved to DB)
        instance = MyModelFactory.build()

        # Create and save an instance to the DB
        saved_instance = MyModelFactory.create()

        # Output for verification
        print("### saved_instance.name:",saved_instance.name,
              "saved_instance.description:", saved_instance.description)


