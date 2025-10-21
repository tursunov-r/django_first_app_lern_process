from django.urls import path, include

from .views import hello_world_view, GroupsListView, ProductsListView, OrdersListView


app_name = "myapiapp"

urlpatterns = [
    path("hello/", hello_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
    path("products/", ProductsListView.as_view(), name="products"),
    path("orders/", OrdersListView.as_view(), name="orders"),
]
