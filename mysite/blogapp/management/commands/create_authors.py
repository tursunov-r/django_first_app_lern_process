from django.core.management import BaseCommand
from blogapp.models import Author


class Command(BaseCommand):
    """
    Creates authors
    """

    def handle(self, *args, **options):
        self.stdout.write("Creating authors...")

        authors_names = [
            "Иван Иванов",
            "Мария Петрова",
            "Алексей Смирнов",
            "Ольга Кузнецова",
        ]

        for name in authors_names:
            author, created = Author.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"Created author: {author.name}")
            else:
                self.stdout.write(f"Author already exists: {author.name}")

        self.stdout.write(self.style.SUCCESS("Authors created successfully!"))
