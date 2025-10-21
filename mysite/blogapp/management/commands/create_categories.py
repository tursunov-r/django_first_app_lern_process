from django.core.management import BaseCommand
from blogapp.models import Category


class Command(BaseCommand):
    """
    Creates categories
    """

    def handle(self, *args, **options):
        self.stdout.write("Creating categories...")

        categories_names = ["Технологии", "Программирование", "Наука", "Образование"]

        for name in categories_names:
            category, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"Created category: {category.name}")
            else:
                self.stdout.write(f"Category already exists: {category.name}")

        self.stdout.write(self.style.SUCCESS("Categories created successfully!"))
