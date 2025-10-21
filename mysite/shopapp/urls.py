from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.cache import cache_page

from .views import (
    ShopIndexView,
    ProductDetailsView,
    ProductsListView,
    OrdersListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductFeed,
    UserOrdersListView,
    export_user_orders,
)

app_name = "shopapp"

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("orders", OrderViewSet)
urlpatterns = [
    # path("", cache_page(60 * 2)(ShopIndexView.as_view()), name="index"),
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(router.urls), name="api"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path(
        "products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"
    ),
    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/create/", OrderCreateView.as_view(), name="create-order"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path(
        "users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders"
    ),
    path(
        "users/<int:user_id>/orders/export/",
        export_user_orders,
        name="export_user_orders",
    ),
    path("products/latest/feed/", LatestProductFeed(), name="latest-product-feed"),
]
