from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)


class BrandModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name="Test brand")

    def test_name_is_unique(self):
        """
        Brands have unique names, testing name uniqueness instead of slug.
        """
        Brand.objects.create(name="Same Name")

        with self.assertRaises(IntegrityError):
            Brand.objects.create(name="Same Name")

    def test_slug_is_generated_from_name(self):
        self.assertEqual(self.brand.slug, "test-brand")

    def test_str_returns_name(self):
        self.assertEqual(str(self.brand), "Test brand")


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test category")

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

    def test_str_returns_name(self):
        self.assertEqual(str(self.category), "Test category")


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")
        cls.product = Product.objects.create(
            brand=cls.brand,
            category=cls.category,
            name="Test product",
            thumbnail=SimpleUploadedFile(name="A.png", content=b"A"),
        )

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

    def test_thumbnail_upload_path(self):
        self.assertIn(
            f"products/{self.product.uuid}/thumbnails/product/",
            self.product.thumbnail.name,
        )

    def test_product_is_active_by_default(self):
        self.assertTrue(self.product.is_active)

    def test_active_returns_only_active_products(self):
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

    def test_str_returns_name(self):
        self.assertEqual(str(self.product), "Test product")


class VariantModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")
        cls.product = Product.objects.create(
            brand=cls.brand, category=cls.category, name="Test product"
        )
        cls.variant = Variant.objects.create(sku="SKU-A", product=cls.product)

    def test_sku_is_globally_unique(self):
        with self.assertRaises(IntegrityError):
            Variant.objects.create(sku="SKU-A", product=self.product)

    def test_variant_is_active_by_default(self):
        self.assertTrue(self.variant.is_active)

    def test_active_returns_only_active_variants(self):
        active_variant = Variant.objects.create(sku="active", product=self.product)
        inactive_variant = Variant.objects.create(
            sku="inactive", is_active=False, product=self.product
        )

        self.assertIn(active_variant, Variant.objects.active())
        self.assertNotIn(inactive_variant, Variant.objects.active())

    def test_str_returns_sku(self):
        self.assertEqual(str(self.variant), "SKU-A")

    def test_primary_image_returns_first_image(self):
        variant = Variant.objects.create(sku="SKU-TEST", product=self.product)

        img2 = VariantImage.objects.create(
            image=SimpleUploadedFile(name="B.png", content=b"B"),
            order=2,
            variant=variant,
        )
        img1 = VariantImage.objects.create(
            image=SimpleUploadedFile(name="A.png", content=b"A"),
            order=1,
            variant=variant,
        )

        self.assertEqual(variant.primary_image, img1)


class VariantImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test brand")
        cls.category = Category.objects.create(name="Test category")
        cls.product = Product.objects.create(
            brand=cls.brand, category=cls.category, name="Test product"
        )

    def test_product_image_upload_path(self):
        variant = Variant.objects.create(sku="SKU-A", product=self.product)

        image = VariantImage.objects.create(variant=variant)
        image.image = SimpleUploadedFile(name="test.png", content=b"test_file_content")
        image.save()

        self.assertIn(
            f"products/{self.product.uuid}/images/variants/{variant.uuid}/",
            image.image.name,
        )

    def test_image_is_active_by_default(self):
        variant = Variant.objects.create(sku="SKU-A", product=self.product)

        image = VariantImage.objects.create(
            image=SimpleUploadedFile(name="A.png", content=b"A"),
            order=1,
            variant=variant,
        )

        self.assertTrue(image.is_active)

    def test_active_returns_only_active_images(self):
        variant = Variant.objects.create(sku="SKU-A", product=self.product)

        active_image = VariantImage.objects.create(
            image=SimpleUploadedFile(name="A.png", content=b"A"),
            variant=variant,
        )
        inactive_image = VariantImage.objects.create(
            image=SimpleUploadedFile(name="B.png", content=b"B"),
            is_active=False,
            variant=variant,
        )

        self.assertIn(active_image, VariantImage.objects.active())
        self.assertNotIn(inactive_image, VariantImage.objects.active())

    def test_product_image_ordering(self):
        variant = Variant.objects.create(sku="SKU-A", product=self.product)

        img2 = VariantImage.objects.create(variant=variant, order=2)
        img1 = VariantImage.objects.create(variant=variant, order=1)

        images = list(variant.images.all())

        self.assertEqual(images[0], img1)
        self.assertEqual(images[1], img2)

    def test_str(self):
        variant = Variant.objects.create(sku="SKU-A", product=self.product)

        image = VariantImage.objects.create(
            image=SimpleUploadedFile(name="A.png", content=b"A"),
            order=1,
            variant=variant,
        )

        self.assertEqual(str(image), "Image for variant: SKU-A #1")
