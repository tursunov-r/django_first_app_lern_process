import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель представляет товары которые можно продавать в интернет магазине.

    Заказы: :model:`shopapp.Order`
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(db_index=True, max_length=100, verbose_name=_("Name"))
    description = models.TextField(
        db_index=True, null=False, blank=True, verbose_name=_("Description")
    )
    price = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Price"),
        validators=[MinValueValidator(0.0)],
    )
    discount = models.SmallIntegerField(
        default=0,
        verbose_name=_("Discount"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived"))
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path,
        verbose_name=_("Preview"),
    )

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse("shopapp:product-detail", kwargs={"pk": self.pk})


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return f"products/product_{instance.product.pk}/images/{filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(
        upload_to=product_images_directory_path, verbose_name=_("Image")
    )
    description = models.CharField(
        max_length=200, blank=True, verbose_name=_("Description")
    )

    def __str__(self):
        return f"ProductImage(pk={self.pk}, product={self.product_id})"


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(
        null=True, blank=True, verbose_name=_("Delivery address")
    )
    promocode = models.CharField(
        max_length=20, null=False, blank=True, verbose_name=_("Promo code")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("User"))
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name=_("Products")
    )
    receipt = models.FileField(
        null=True, blank=True, upload_to="orders/receipts", verbose_name=_("Receipt")
    )

    def __str__(self):
        return f"Order(pk={self.pk}, user={self.user.username!r})"
