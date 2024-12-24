from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'This command is for testing purposes. It will print a test hello message to the console'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Hello, World!"))

