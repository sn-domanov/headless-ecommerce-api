from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.products.api.v1.serializers import CategorySerializer
from apps.products.models import Brand, Category, Product

User = get_user_model()


class CategorySerializerTest(TestCase):
    def test_category_serializer_parent_name(self):
        parent = Category.objects.create(name="Parent")
        child = Category.objects.create(name="Child", parent=parent)
        serialized = CategorySerializer(child).data
        self.assertEqual(serialized["parent_name"], "Parent")


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="b")
        self.category = Category.objects.create(name="c")

        self.product_active = Product.objects.create(
            name="Active", brand=self.brand, category=self.category, is_active=True
        )
        self.product_inactive = Product.objects.create(
            name="Inactive", brand=self.brand, category=self.category, is_active=False
        )

    def test_public_products_only_active(self):
        response = self.client.get("/api/v1/products/")
        data = response.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Active")

    def test_products_endpoint_smoke(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, 200)
