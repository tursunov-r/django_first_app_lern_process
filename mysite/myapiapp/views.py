from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin

from .serializers import GroupSerializer, ProductSerializer, OrderSerializer
from shopapp.models import Product, Order


# Create your views here.
@api_view(["GET"])
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello world"})


# class GroupsListView(GenericAPIView):
#     def get(self, request: Request) -> Response:
#         groups = Group.objects.all()
#         serialize = GroupSerializer(groups, many=True)
#         return Response({"groups": serialize.data})


class GroupsListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProductsListView(GenericAPIView):
    def get(self, request: Request) -> Response:
        products = Product.objects.all()
        serialize = ProductSerializer(products, many=True)
        return Response({"products": serialize.data})


class OrdersListView(GenericAPIView):
    def get(self, request: Request) -> Response:
        orders = Order.objects.all()
        serialize = OrderSerializer(orders, many=True)
        return Response({"orders": serialize.data})
