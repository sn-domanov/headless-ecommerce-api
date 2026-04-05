from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from apps.products.models import VariantImage


@extend_schema_serializer(exclude_fields=("is_active",))
class VariantImageBaseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = [
            "uuid",
            "image",
            "alt_text",
            "order",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Using custom property in the viewset to hide internal fields
        view = self.context.get("view")
        if not bool(view and view._is_staff):
            self.fields.pop("is_active", None)


# Reserved for internal use
class VariantImageListSerializer(VariantImageBaseReadSerializer):
    pass


class VariantImageDetailSerializer(VariantImageBaseReadSerializer):
    variant_uuid = serializers.UUIDField(source="variant.uuid", read_only=True)
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)

    class Meta(VariantImageBaseReadSerializer.Meta):
        fields = VariantImageBaseReadSerializer.Meta.fields + [
            "variant_uuid",
            "variant_sku",
        ]


class VariantImageBaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = [
            "image",
            "alt_text",
            "order",
            "variant",
        ]


class VariantImageCreateSerializer(VariantImageBaseWriteSerializer):
    pass


class VariantImageUpdateSerializer(VariantImageBaseWriteSerializer):
    class Meta(VariantImageBaseWriteSerializer.Meta):
        fields = VariantImageBaseWriteSerializer.Meta.fields + [
            "is_active",
        ]
