from io import BytesIO
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import serializers

from apps.products.api.v1.serializers import (
    CategoryDetailSerializer,
    CategoryWriteSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
    VariantCreateSerializer,
    VariantDetailSerializer,
    VariantImageCreateSerializer,
    VariantImageDetailSerializer,
    VariantImageUpdateSerializer,
    VariantUpdateSerializer,
)
from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)


def create_test_image():
    file = BytesIO()
    image = Image.new("RGB", (1, 1))
    image.save(file, "PNG")
    file.seek(0)

    return SimpleUploadedFile(
        "test.png",
        file.read(),
        content_type="image/png",
    )


class CategorySerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Category.add_root(name="Root")
        cls.child = cls.root.add_child(name="Child")

    def test_root_node_has_no_parent(self):
        serializer = CategoryDetailSerializer(self.root)
        data = serializer.data

        self.assertIsNone(data["parent_slug"])
        self.assertIsNone(data["parent_name"])

    def test_child_node_has_parent(self):
        serializer = CategoryDetailSerializer(self.child)
        data = serializer.data

        self.assertEqual(data["parent_slug"], "root")
        self.assertEqual(data["parent_name"], "Root")

    def test_category_create_serializer_valid(self):
        data = {
            "name": "Grandchild",
            "parent": self.child.pk,
        }
        serializer = CategoryWriteSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_category_update_serializer_invalid(self):
        sibling = self.root.add_child(name="Sibling")
        data = {
            "parent": self.child.pk,
        }

        serializer = CategoryWriteSerializer(instance=sibling, data=data, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("parent", serializer.errors)
        self.assertEqual(
            serializer.errors["parent"][0], "Changing parent is not allowed"
        )


class ProductSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name="Test Brand")
        cls.category = Category.add_root(name="Root Category")

        cls.product = Product.objects.create(
            name="Test Product",
            description="Test description",
            brand=cls.brand,
            category=cls.category,
        )

        cls.variant = Variant.objects.create(product=cls.product, sku="sku1")

        cls.img2 = VariantImage.objects.create(
            image=create_test_image(),
            order=2,
            variant=cls.variant,
        )
        cls.img1 = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            variant=cls.variant,
        )

    def test_product_read_serializers_include_nested_serializers(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data

        self.assertEqual(data["brand"]["slug"], "test-brand")
        self.assertEqual(data["brand"]["name"], "Test Brand")

        self.assertEqual(data["category"]["slug"], "root-category")
        self.assertEqual(data["category"]["name"], "Root Category")

    def test_product_read_serializers_hide_is_active_for_non_staff(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data

        self.assertNotIn("is_active", data)
        self.assertEqual(data["slug"], "test-product")

    def test_product_read_serializers_show_is_active_for_staff(self):
        serializer = ProductDetailSerializer(
            self.product, context={"view": SimpleNamespace(_is_staff=True)}
        )
        data = serializer.data

        self.assertIn("is_active", data)
        self.assertTrue(data["is_active"])

    def test_product_list_serializer_includes_variants_count(self):
        serializer = ProductListSerializer(self.product)

        # Mock queryset annotation
        serializer.instance.variants_count = (  # pyright: ignore[reportOptionalMemberAccess]
            1
        )
        data = serializer.data

        self.assertIn("variants_count", data)
        self.assertEqual(data["variants_count"], 1)

    def test_product_detail_serializer_includes_variants(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data

        self.assertIn("variants", data)
        self.assertEqual(len(data["variants"]), 1)
        self.assertEqual(data["variants"][0]["sku"], "sku1")

    def test_product_detail_serializer_includes_primary_image(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data

        self.assertEqual(data["variants"][0]["image"]["uuid"], str(self.img1.uuid))

    def test_product_write_serializers_include_correct_fields(self):
        create_fields = ProductCreateSerializer.Meta.fields
        update_fields = ProductUpdateSerializer.Meta.fields

        self.assertNotIn("is_active", create_fields)
        self.assertIn("is_active", update_fields)

    def test_product_create_serializer_valid(self):
        data = {
            "name": "New Product",
            "description": "Desc",
            "brand": self.brand.pk,
            "category": self.category.pk,
        }
        serializer = ProductCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)


class VariantSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name="Test Brand")
        cls.category = Category.add_root(name="Root Category")

        cls.product = Product.objects.create(
            name="Test Product",
            description="Test description",
            brand=cls.brand,
            category=cls.category,
        )

        cls.variant = Variant.objects.create(product=cls.product, sku="sku1")

        cls.img2 = VariantImage.objects.create(
            image=create_test_image(),
            order=2,
            variant=cls.variant,
        )
        cls.img1 = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            variant=cls.variant,
        )

    def test_variant_read_serializers_include_nested_serializers(self):
        serializer = VariantDetailSerializer(self.variant)
        data = serializer.data

        self.assertIn("images", data)
        self.assertEqual(len(data["images"]), 2)
        self.assertEqual(data["images"][0]["uuid"], str(self.img1.uuid))

        self.assertIn("product", data)
        self.assertEqual(data["product"]["slug"], "test-product")

    def test_variant_read_serializers_hide_is_active_for_non_staff(self):
        serializer = VariantDetailSerializer(self.variant)
        data = serializer.data

        self.assertNotIn("is_active", data)
        self.assertEqual(data["sku"], "sku1")

    def test_variant_read_serializers_show_is_active_for_staff(self):
        serializer = VariantDetailSerializer(
            self.variant, context={"view": SimpleNamespace(_is_staff=True)}
        )
        data = serializer.data

        self.assertIn("is_active", data)
        self.assertTrue(data["is_active"])

    def test_variant_write_serializers_include_correct_fields(self):
        create_fields = VariantCreateSerializer.Meta.fields
        update_fields = VariantUpdateSerializer.Meta.fields

        self.assertNotIn("is_active", create_fields)
        self.assertIn("is_active", update_fields)

    def test_variant_create_serializer_valid(self):
        data = {
            "sku": "sku2",
            "product": self.product.pk,
        }
        serializer = VariantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class VariantImageSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name="Test Brand")
        cls.category = Category.add_root(name="Root Category")
        cls.product = Product.objects.create(
            name="Test Product",
            description="Test description",
            brand=cls.brand,
            category=cls.category,
        )
        cls.variant = Variant.objects.create(product=cls.product, sku="sku1")

        cls.img = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            variant=cls.variant,
        )

    def test_variant_image_read_serializers_hide_is_active_for_non_staff(self):
        serializer = VariantImageDetailSerializer(self.img)
        data = serializer.data

        self.assertNotIn("is_active", data)
        self.assertEqual(data["uuid"], str(self.img.uuid))

    def test_variant_image_read_serializers_show_is_active_for_staff(self):
        serializer = VariantImageDetailSerializer(
            self.img, context={"view": SimpleNamespace(_is_staff=True)}
        )
        data = serializer.data

        self.assertIn("is_active", data)
        self.assertTrue(data["is_active"])

    def test_variant_image_write_serializers_include_correct_fields(self):
        create_fields = VariantImageCreateSerializer.Meta.fields
        update_fields = VariantImageUpdateSerializer.Meta.fields

        self.assertNotIn("is_active", create_fields)
        self.assertIn("is_active", update_fields)

    def test_variant_image_create_serializer_valid(self):
        data = {
            "image": create_test_image(),
            "order": 1,
            "variant": self.variant.pk,
        }

        serializer = VariantImageCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
