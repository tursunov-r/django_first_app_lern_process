from random import randint
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write("Create products")

        products_names = [
            "Laptop",
            "Desktop",
            "Smartphone",
        ]
        for products_name in products_names:
            product, created = Product.objects.get_or_create(
                name=products_name, price=randint(100, 1000), discount=randint(0, 25)
            )
            self.stdout.write(f"Created product {product.name}")

        self.stdout.write(self.style.SUCCESS("Products created"))
