from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregation")

        # result = Product.objects.filter(name__contains="Smartphone").aggregate(
        #     Avg("price"),
        #     Max("price"),
        #     Min("price"),
        #     Count("id"),
        # )
        # print(result)

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products"),
        )
        for order in orders:
            print(
                f"Order #{order.id}",
                f"With {order.products_count}",
                f"Products worth {order.total}",
            )
        self.stdout.write(self.style.SUCCESS("Products created"))
