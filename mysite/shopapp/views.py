"""В этом модуле описаны представления (views) для приложения shopapp."""

import logging
from timeit import default_timer
from csv import DictWriter

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import User
from django.contrib.gis.feeds import Feed
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    Http404,
)
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.request import Request

from .forms import OrderForm, ProductForm
from .models import Order, Product, ProductImage
from .serializers import OrderSerializer, ProductSerializer
from .command import save_csv_products


log = logging.getLogger(__name__)


def export_user_orders(request, user_id: int):
    """
    Для экспорта заказов конкретного пользователя в JSON.
    Результат кешируется для ускорения повторных запросов.
    """

    # Генерируем уникальный ключ кеша для пользователя
    cache_key = f"user_orders_export_{user_id}"

    # Пытаемся загрузить данные из кеша
    cached_data = cache.get(cache_key)
    if cached_data:
        # Данные найдены в кеше → возвращаем их сразу
        return JsonResponse(cached_data, safe=False)

    user = get_object_or_404(User, pk=user_id)

    orders = Order.objects.filter(user=user).order_by("pk")

    # список словарей с нужными полями
    data = [
        {
            "id": order.id,
            "delivery_address": order.delivery_address,
            "promocode": order.promocode,
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]

    cache.set(cache_key, data, timeout=300)

    # Возвращаем JSON-ответ
    return JsonResponse(data, safe=False)


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shopapp/user_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        try:
            self.owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")

        # Фильтруем заказы по выбранному пользователю
        return Order.objects.filter(user=self.owner).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context


class LatestProductFeed(Feed):
    title = "Product Feed"
    description = "Update product"
    link = reverse_lazy("shopapp:product-list")

    def items(self):
        return Product.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


@extend_schema(description="Products Views CRUD")
class ProductViewSet(ModelViewSet):
    """
    ViewSet обеспечивает CRUD-операции для модели Product.

    Включает функции фильтрации, поиска и упорядочивания.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("name", "description")
    filterset_fields = ["name", "description", "price", "discount", "archived"]
    ordering_fields = ["name", "price", "discount"]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(detail=False, methods=["get"])
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = f"products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})
        return response

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            file=request.FILES["file"].file, encoding=request.encoding
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Возвращает продукт, 404 если не найден.",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Product by id not found"),
        },
    )
    def retrieve(self, *args, **kwargs):
        """Return a single product by its ID."""
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    """CRUD ViewSet для модели Order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    search_fields = ("user", "delivery_address")
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filterset_fields = [
        "user",
        "delivery_address",
        "promocode",
        "created_at",
    ]
    ordering_fields = [
        "user",
        "delivery_address",
        "promocode",
        "created_at",
    ]


class ShopIndexView(View):
    """Главная страница магазина."""

    # @method_decorator(cache_page(60))
    def get(self, request: HttpRequest) -> HttpResponse:
        """Render index page with basic product list."""
        products = [
            ("Laptop", 1999),
            ("Desktop", 2999),
            ("Smartphone", 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Shop index page with basic product list")
        print(f"shop index context {context}")
        return render(request, "shopapp/shop-index.html", context=context)


class ProductDetailsView(DetailView):
    """Детали конкретного продукта."""

    template_name = "shopapp/products-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    """Список всех активных продуктов."""

    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    """Создание нового продукта с изображениями."""

    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        """Handle product creation with uploaded images."""
        response = super().form_valid(form)
        for image in self.request.FILES.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response


class ProductUpdateView(UpdateView):
    """Редактирование продукта."""

    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса на обновление продукта."""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        """Обработка обновления товара и загрузки изображения."""
        response = super().form_valid(form)
        for image in self.request.FILES.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response

    def get_success_url(self):
        """Возврат URL-адреса перенаправления после успешного обновления."""
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    """Архивация (удаление) продукта."""

    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        """Отметить продукт как архивный вместо удаления."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    """Список заказов пользователя."""

    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderCreateView(CreateView):
    """Создание нового заказа."""

    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    """Редактирование заказа."""

    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders")
    template_name_suffix = "_update_form"

    def get_success_url(self):
        """Возвращает URL-адрес перенаправления после успешного обновления."""
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """Просмотр деталей заказа (требует разрешения)."""

    permission_required = "shopapp.view_order"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderDeleteView(DeleteView):
    """Удаление заказа."""

    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class ProductsDataExportView(View):
    """Экспорт списка продуктов в формате JSON."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Возврат список JSON для всех товаров."""
        cache_key = f"product_data_cache_key"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})
