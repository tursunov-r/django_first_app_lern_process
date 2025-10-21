import csv
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .command import save_csv_products
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = ProductImage


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archive products")
def mark_archived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "admin/products-changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    # list_display = "pk", "name", "description", "price", "discount"
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price options",
            {
                "fields": ("price", "discount"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "Images",
            {"fields": ("preview",)},
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description": "Extra options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form}
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {"form": form}
            return render(request, "admin/csv_form.html", context, status=400)

        save_csv_products(file=form.files["csv_file"].file, encoding=request.encoding)
        self.message_user(request, "Successfully imported products.")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-products-csv/", self.import_csv, name="import_products_csv"),
        ] + urls
        return new_urls + urls


# admin.site.register(Product, ProductAdmin)


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders_changelist.html"
    list_display = ("delivery_address", "promocode", "created_at", "user_verbose")

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    # ---- Импорт заказов ----
    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form, "title": "Import orders from CSV"}
            return render(request, "admin/csv_form.html", context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {"form": form, "title": "Error importing orders in form"}
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = form.cleaned_data["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        for row in reader:
            # ожидаем, что CSV содержит поля: user_id, delivery_address, promocode, product_ids
            user_id = row.get("user_id")
            delivery_address = row.get("delivery_address", "")
            promocode = row.get("promocode", "")
            product_ids = row.get("product_ids", "")

            order = Order.objects.create(
                user_id=user_id,
                delivery_address=delivery_address,
                promocode=promocode,
            )

            if product_ids:
                ids = [
                    int(pid.strip()) for pid in product_ids.split(",") if pid.strip()
                ]
                products = Product.objects.filter(id__in=ids)
                order.products.set(products)

            created_count += 1

        self.message_user(request, f"Success import {created_count} orders.")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-orders-csv/", self.import_csv, name="import_orders_csv"),
        ]
        return new_urls + urls
