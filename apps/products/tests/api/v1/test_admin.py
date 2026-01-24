from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.products.models import Brand, Category, Product

User = get_user_model()


class ProductAdminViewSetTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="pass"
        )
        self.user = User.objects.create_user(email="user@example.com", password="pass")

        self.brand = Brand.objects.create(name="b")
        self.category = Category.objects.create(name="c")

        self.product_active = Product.objects.create(
            name="Active", brand=self.brand, category=self.category, is_active=True
        )
        self.product_inactive = Product.objects.create(
            name="Inactive", brand=self.brand, category=self.category, is_active=False
        )

    def test_admin_sees_all_products(self):
        self.client.login(email="admin@example.com", password="pass")
        response = self.client.get("/api/v1/admin/products/")
        names = [p["name"] for p in response.json()["results"]]
        self.assertIn("Active", names)
        self.assertIn("Inactive", names)

    def test_non_admin_cannot_access_admin_products(self):
        self.client.login(email="user@example.com", password="pass")
        response = self.client.get("/api/v1/admin/products/")
        self.assertEqual(response.status_code, 403)
