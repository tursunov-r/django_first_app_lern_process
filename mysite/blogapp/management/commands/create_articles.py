from random import randint, choice
from django.core.management import BaseCommand
from django.utils import timezone

from blogapp.models import Article, Author, Category, Tag


class Command(BaseCommand):
    """
    Creates articles
    """

    def handle(self, *args, **options):
        self.stdout.write("Creating articles...")

        # Заготовки для заголовков и контента
        titles = [
            "Как научиться Django",
            "Лучшие практики Python",
            "Введение в веб-разработку",
            "Советы по оптимизации кода",
            "Работа с базой данных",
        ]

        contents = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Praesent commodo cursus magna, vel scelerisque nisl consectetur.",
            "Curabitur blandit tempus porttitor.",
            "Integer posuere erat a ante venenatis dapibus posuere velit aliquet.",
            "Donec sed odio dui.",
        ]

        authors = list(Author.objects.all())
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())

        if not authors or not categories:
            self.stdout.write(self.style.ERROR("Создайте сначала авторов и категории!"))
            return

        for i in range(len(titles)):
            article, created = Article.objects.get_or_create(
                title=titles[i],
                defaults={
                    "content": contents[i % len(contents)],
                    "pub_date": timezone.now(),
                    "author": choice(authors),
                    "category": choice(categories),
                },
            )
            if created:
                # Добавляем случайные теги
                selected_tags = [
                    choice(tags) for _ in range(randint(0, min(3, len(tags))))
                ]
                article.tags.set(selected_tags)
                article.save()
                self.stdout.write(f"Created article: {article.title}")
            else:
                self.stdout.write(f"Article already exists: {article.title}")

        self.stdout.write(self.style.SUCCESS("Articles created successfully!"))
