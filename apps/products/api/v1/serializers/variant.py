from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from apps.products.models import Variant

from .nested import ProductNestedSerializer, VariantImageNestedSerializer


@extend_schema_serializer(exclude_fields=("is_active",))
class VariantBaseReadSerializer(serializers.ModelSerializer):
    images = VariantImageNestedSerializer(many=True, read_only=True)
    product = ProductNestedSerializer(read_only=True)

    class Meta:
        model = Variant
        fields = [
            "uuid",
            "sku",
            "is_digital",
            "images",
            "product",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Using custom property in the viewset to disallow fields
        view = self.context.get("view")
        if not bool(view and view._is_staff):
            self.fields.pop("is_active", None)


# Reserved for internal use (inventory, bulk management, etc.)
class VariantListSerializer(VariantBaseReadSerializer):
    pass


# Reserved for product variant information from other domains (price, stock, availability, etc.)
class VariantDetailSerializer(VariantBaseReadSerializer):
    pass


class VariantBaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        # Leaving `is_active` True by default for `create` action
        fields = [
            "sku",
            "is_digital",
            "product",
        ]


class VariantCreateSerializer(VariantBaseWriteSerializer):
    pass


class VariantUpdateSerializer(VariantBaseWriteSerializer):
    class Meta(VariantBaseWriteSerializer.Meta):
        fields = VariantBaseWriteSerializer.Meta.fields + [
            "is_active",
        ]
