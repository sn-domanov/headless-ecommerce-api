from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Brand, Category, Product

User = get_user_model()


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.list_url = reverse("products-list")

        # Users
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="pass",
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
        )

        # Related objects
        self.brand = Brand.objects.create(name="Brand")
        self.category = Category.objects.create(name="Category")

        # Products
        self.active_product = Product.objects.create(
            name="Active",
            description="Active",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            name="Inactive",
            description="Inactive",
            brand=self.brand,
            category=self.category,
            is_active=False,
        )

        # Reusable payload
        self.create_payload = {
            "name": "New",
            "description": "New",
            "brand": self.brand.pk,
            "category": self.category.pk,
            "is_active": True,
        }

    # Read tests
    def test_products_endpoint_smoke(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_sees_only_active_products(self):
        response = self.client.get(self.list_url)

        names = [p["name"] for p in response.data["results"]]

        self.assertIn(self.active_product.name, names)
        self.assertNotIn(self.inactive_product.name, names)

    def test_admin_sees_all_products(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]

        self.assertIn(self.active_product.name, names)
        self.assertIn(self.inactive_product.name, names)

    def test_category_filter_includes_descendants_products(self):
        parent = Category.objects.create(name="parent")
        child = Category.objects.create(name="child", parent=parent)
        grandchild = Category.objects.create(name="grandchild", parent=child)
        product_a = Product.objects.create(
            name="A",
            description="A",
            brand=self.brand,
            category=parent,
            is_active=True,
        )
        product_b = Product.objects.create(
            name="B",
            description="B",
            brand=self.brand,
            category=child,
            is_active=True,
        )
        product_c = Product.objects.create(
            name="C",
            description="C",
            brand=self.brand,
            category=grandchild,
            is_active=True,
        )

        response = self.client.get(self.list_url, {"category": parent.slug})
        names = [p["name"] for p in response.data["results"]]

        self.assertIn(product_a.name, names)
        self.assertIn(product_b.name, names)
        self.assertIn(product_c.name, names)

    def test_category_filter_excludes_parent_products(self):
        parent = Category.objects.create(name="parent")
        child = Category.objects.create(name="child", parent=parent)
        product_a = Product.objects.create(
            name="A",
            description="A",
            brand=self.brand,
            category=parent,
            is_active=True,
        )

        product_b = Product.objects.create(
            name="B",
            description="B",
            brand=self.brand,
            category=child,
            is_active=True,
        )

        response = self.client.get(self.list_url, {"category": child.slug})
        names = [p["name"] for p in response.data["results"]]

        self.assertNotIn(product_a.name, names)
        self.assertIn(product_b.name, names)

    def test_invalid_category_filter_returns_empty_list(self):
        category = Category.objects.create(name="A")
        product_a = Product.objects.create(
            name="A",
            description="A",
            brand=self.brand,
            category=category,
            is_active=True,
        )

        response = self.client.get(self.list_url, {"category": "B"})

        self.assertEqual(response.data["results"], [])

    # Write tests
    def test_non_admin_cannot_create_product(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
