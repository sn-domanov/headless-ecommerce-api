from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import Brand, Category, Product, ProductImage


class BrandModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name="Test brand")

    def test_str_returns_name(self):
        self.assertEqual(str(self.brand), "Test brand")

    def test_slug_is_generated_from_name(self):
        self.assertEqual(self.brand.slug, "test-brand")

    def test_name_is_unique(self):
        """
        Brands have unique names, testing name uniqueness instead of slug.
        """
        Brand.objects.create(name="Same Name")

        with self.assertRaises(IntegrityError):
            Brand.objects.create(name="Same Name")


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test category")

    def test_str_returns_name(self):
        self.assertEqual(str(self.category), "Test category")

    def test_slug_is_generated_from_name(self):
        self.assertEqual(self.category.slug, "test-category")

    def test_slug_is_unique(self):
        first = Category.objects.create(name="Same Name")
        second = Category.objects.create(name="Same Name")

        self.assertNotEqual(first.slug, second.slug)

    def test_category_hierarchy(self):
        root = Category.objects.create(name="Root")
        child = Category.objects.create(name="Child", parent=root)
        self.assertEqual(child.parent, root)
        self.assertIn(child, root.children.all())


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")
        cls.product = Product.objects.create(
            category=cls.category,
            brand=cls.brand,
            name="Test product",
        )

    def test_str_returns_name(self):
        self.assertEqual(str(self.product), "Test product")

    def test_slug_is_generated_from_name(self):
        self.assertEqual(self.product.slug, "test-product")

    def test_slug_is_unique(self):
        first = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Same Name",
        )
        second = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Same Name",
        )

        self.assertNotEqual(first.slug, second.slug)

    def test_product_is_active_by_default(self):
        self.assertTrue(self.product.is_active)

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


class ProductImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")

    def test_str(self):
        product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Image Test",
        )

        image = ProductImage.objects.create(product=product)
        self.assertEqual(str(image), "Image Test image #1")

    def test_product_image_upload_path(self):
        product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Image Test",
        )

        image = ProductImage.objects.create(product=product)
        image.image = SimpleUploadedFile(name="test.webp", content=b"test_file_content")
        image.save()

        self.assertIn(f"products/images/{product.slug}/", image.image.name)

    def test_product_image_ordering(self):
        product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Ordering Test",
        )

        img1 = ProductImage.objects.create(product=product, order=2)
        img2 = ProductImage.objects.create(product=product, order=1)

        images = list(product.images.all())

        self.assertEqual(images[0], img2)
        self.assertEqual(images[1], img1)
