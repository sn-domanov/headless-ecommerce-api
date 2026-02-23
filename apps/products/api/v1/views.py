from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

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


class ProductViewSet(viewsets.ModelViewSet):
    def _is_admin(self) -> bool:
        return bool(self.request.user and self.request.user.is_staff)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    # N.B. Using method also avoids accidental queryset reuse if the class is subclassed later
    def get_queryset(self):
        if self._is_admin():
            return Product.objects.all()
        return Product.objects.active()

    def get_serializer_class(self):
        if self._is_admin():
            return ProductAdminSerializer
        return ProductSerializer
