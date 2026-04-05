from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from apps.products.models import Product

from .nested import (
    BrandNestedSerializer,
    CategoryNestedSerializer,
    VariantNestedSerializer,
)


@extend_schema_serializer(exclude_fields=("is_active",))
class ProductBaseReadSerializer(serializers.ModelSerializer):
    brand = BrandNestedSerializer(read_only=True)
    category = CategoryNestedSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "slug",
            "uuid",
            "name",
            "thumbnail",
            "brand",
            "category",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Using custom property in the viewset to hide internal fields
        view = self.context.get("view")
        if not bool(view and view._is_staff):
            self.fields.pop("is_active", None)


class ProductListSerializer(ProductBaseReadSerializer):
    variants_count = serializers.IntegerField()

    class Meta(ProductBaseReadSerializer.Meta):
        fields = ProductBaseReadSerializer.Meta.fields + [
            "variants_count",
        ]


class ProductDetailSerializer(ProductBaseReadSerializer):
    variants = VariantNestedSerializer(many=True, read_only=True)

    class Meta(ProductBaseReadSerializer.Meta):
        model = Product
        fields = ProductBaseReadSerializer.Meta.fields + [
            "description",
            "variants",
        ]


class ProductBaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # Leaving `is_active` by default (True) for `create` action
        fields = [
            "name",
            "description",
            "thumbnail",
            "category",
            "brand",
        ]


class ProductCreateSerializer(ProductBaseWriteSerializer):
    pass


class ProductUpdateSerializer(ProductBaseWriteSerializer):
    class Meta(ProductBaseWriteSerializer.Meta):
        fields = ProductBaseWriteSerializer.Meta.fields + [
            "is_active",
        ]
