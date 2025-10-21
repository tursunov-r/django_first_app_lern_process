from typing import Sequence

from django.core.management import BaseCommand
from django.contrib.auth.models import User

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo selected fields")
        users = User.objects.values_list("username", flat=True)
        product_values = Product.objects.values("pk", "name")

        for user in users:
            print(user)

        for p in product_values:
            print(p)

        self.stdout.write(self.style.SUCCESS(f"DONE"))
