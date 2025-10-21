from random import choice
from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        # products: Sequence[Product] = Product.objects.defer(
        #     "description", "price", "created_at"
        # ).all()
        products: Sequence[Product] = Product.objects.only(
            "id",
        ).all()
        order, created = Order.objects.get_or_create(
            delivery_address="st. Lenin 56",
            promocode="promocode1",
            user=user,
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(self.style.SUCCESS(f"SUCCESS: Creating order{order}"))


# class Command(BaseCommand):
#     help = "Создаёт тестовый заказ для пользователя admin"
#
#     def handle(self, *args, **options):
#         self.stdout.write("Создаю заказ...")
#
#         # Получаем продукты
#         products = list(Product.objects.all())
#         if not products:
#             self.stdout.write(self.style.WARNING("Нет доступных продуктов!"))
#             return
#
#         # Получаем пользователя admin
#         try:
#             user = User.objects.get(username="admin")
#         except User.DoesNotExist:
#             self.stdout.write(self.style.ERROR("Пользователь 'admin' не найден!"))
#             return
#
#         products: Sequence[Product] = Product.objects.all()
#         # Создаём заказ
#         order, created = Order.objects.get_or_create(
#             delivery_address="ул. Пупкина, д. 8",
#             promocode="SALE123",
#             user=user,
#         )
#
#         # Добавляем случайные продукты в заказ
#         selected_products = [choice(products) for _ in range(3)]
#         order.products.set(selected_products)
#
#         order.save()
#
#         if created:
#             msg = f"Создан новый заказ #{order.id} для пользователя {user.username}"
#         else:
#             msg = f"Использован существующий заказ #{order.id}"
#
#         self.stdout.write(self.style.SUCCESS(msg))
