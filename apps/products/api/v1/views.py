from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from apps.products.api.v1.serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductAdminSerializer,
    ProductSerializer,
)
from apps.products.models import Brand, Category, Product


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    # Disable the default pagination set in config.settings.base
    pagination_class = None


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.active()
    serializer_class = ProductSerializer


class ProductAdminViewSet(viewsets.ModelViewSet):
    serializer_class = ProductAdminSerializer
    permission_classes = [IsAdminUser]

    # Avoid accidental queryset reuse if the class is subclassed later
    def get_queryset(self):
        return Product.objects.all()
