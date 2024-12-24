from django.core.management.base import BaseCommand
from myapp.models import MyModel
from django.utils import timezone
import time
from model_bakery import baker
from faker import Faker


class Command(BaseCommand):
    help = 'This command will create a MyModel object with fake data using Model Bakery'

    def handle(self, *args, **options):
        # region raw model_bakery usage
        # Create a single instance of MyModel with random data
        instance = baker.make(MyModel)

        # Create a batch of instances
        instances = baker.make(MyModel, _quantity=5)

        # Customizing fields
        custom_instance = baker.make(MyModel, name="Custom Name", description="Custom Description")
        # endregion
        # region combining model_bakery with faker
        faker = Faker()
        # it still repeats the same data for all instances
        # improved_instances = baker.make(MyModel, _quantity=5, name=faker.name(), description=faker.text())
        # it generates unique data for each instance
        improved_instances = baker.make(MyModel, _quantity=5, name=lambda: faker.unique.name(), description=lambda: faker.unique.text())
        # endregion

        # Output for verification
        print("### instance.name:", instance.name,
              "instance.description:", instance.description)
        print("### instances:")
        print([f"obj.name:  {obj.name} obj.description: {obj.description}" for obj in instances], end="\n\n")
        print("### improved_instances:")
        print([f"improved_obj.name:  {improved_obj.name} improved_obj.description: {improved_obj.description}" for improved_obj in improved_instances], end="\n\n")
        print("### custom_instance.name:", custom_instance.name,
              "custom_instance.description:", custom_instance.description)



