from rest_framework import serializers

from apps.products.models import Brand, Category, Product


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "parent_name"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "brand", "is_digital"]


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
