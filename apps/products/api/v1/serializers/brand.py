from rest_framework import serializers

from apps.products.models import Brand


class BrandBaseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "slug",
            "name",
        ]


class BrandListSerializer(BrandBaseReadSerializer):
    pass


class BrandDetailSerializer(BrandBaseReadSerializer):
    pass


class BrandWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "name",
        ]
