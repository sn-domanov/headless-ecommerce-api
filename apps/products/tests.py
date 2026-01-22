from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import Brand, Category, Product


class BrandModelTestCase(TestCase):
    def test_str_returns_name(self):
        brand = Brand.objects.create(name="Test brand")
        self.assertEqual(str(brand), "Test brand")


class CategoryModelTestCase(TestCase):
    def test_str_returns_name(self):
        category = Category.objects.create(name="Test category")
        self.assertEqual(str(category), "Test category")

    def test_category_hierarchy(self):
        root = Category.objects.create(name="Root")
        child = Category.objects.create(name="Child", parent=root)
        self.assertEqual(child.parent, root)
        self.assertIn(child, root.children.all())

    def test_unique_category_per_parent(self):
        root = Category.objects.create(name="Root")
        Category.objects.create(name="Child", parent=root)
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Child", parent=root)


class ProductModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")

    def test_str_returns_name(self):
        product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Test product",
        )
        self.assertEqual(str(product), "Test product")

    def test_product_is_active_by_default(self):
        product = Product.objects.create(
            name="Test product",
            category=self.category,
            brand=self.brand,
        )
        self.assertTrue(product.is_active)

    def test_active_queryset_returns_only_active_products(self):
        active_product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Active product",
            is_active=True,
        )
        inactive_product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Inactive product",
            is_active=False,
        )

        self.assertIn(active_product, Product.objects.active())
        self.assertNotIn(inactive_product, Product.objects.active())
