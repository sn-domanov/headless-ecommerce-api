from rest_framework import serializers

from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)


class BrandNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "slug",
            "name",
        ]


class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "slug",
            "name",
        ]


class ProductNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "slug",
            "name",
        ]


class VariantImageNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = [
            "uuid",
            "image",
            "alt_text",
            "order",
        ]


class VariantNestedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = [
            "uuid",
            "sku",
            "is_digital",
            "image",
        ]

    def get_image(self, obj):
        image = obj.primary_image
        return VariantImageNestedSerializer(image).data if image else None
