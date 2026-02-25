from rest_framework import serializers

from apps.products.models import Brand, Category, Product


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "slug", "name"]


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "slug", "name", "parent", "parent_name"]


class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "name"]


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategoryBriefSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "category",
            "brand",
            "is_digital",
        ]


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
