from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)

User = get_user_model()


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


class BrandViewSetTest(APITestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

        # Brands
        self.brand = Brand.objects.create(name="Brand")

        # URLs
        self.list_url = reverse("brands-list")
        self.detail_url = reverse("brands-detail", kwargs={"slug": self.brand.slug})

        # Reusable payload
        self.create_payload = {
            "name": "New",
        }

    # Read tests
    def test_query_count(self):
        self.client.force_authenticate(self.staff)

        with self.assertNumQueries(1):
            self.client.get(self.list_url)

    # Write tests
    def test_non_staff_cannot_create_brand(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_brand(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Brand.objects.count(), 2)

    def test_create_returns_detail_serializer(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertIn("slug", response.data)
        self.assertIn("name", response.data)


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

        # Categories
        self.root = Category.add_root(name="Root")
        self.child = self.root.add_child(name="Child")
        self.grandchild = self.child.add_child(name="Grandchild")

        # URLs
        self.list_url = reverse("categories-list")
        self.detail_url = reverse("categories-detail", kwargs={"slug": self.root.slug})

        # Reusable payload
        self.create_payload = {
            "name": "New",
            "parent": self.root.pk,
        }

    # Write tests
    def test_non_staff_cannot_create_category(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_category(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 4)

    def test_moving_node_is_forbidden(self):
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            self.detail_url, data={"parent": self.grandchild.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["parent"][0], "Changing parent is not allowed")

    def test_create_returns_detail_serializer(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertIn("parent_slug", response.data)
        self.assertIn("parent_name", response.data)


class ProductViewSetTest(APITestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

        # Related objects
        self.brand = Brand.objects.create(name="Brand")
        self.category = Category.add_root(name="Category")

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

        # Variants
        self.active_variant = Variant.objects.create(
            sku="sku-active",
            product=self.active_product,
            is_active=True,
        )
        self.inactive_variant = Variant.objects.create(
            sku="sku-inactive",
            product=self.active_product,
            is_active=False,
        )

        # Variant images
        self.active_img = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            is_active=True,
            variant=self.active_variant,
        )
        self.inactive_img = VariantImage.objects.create(
            image=create_test_image(),
            order=2,
            is_active=False,
            variant=self.active_variant,
        )

        # URLs
        self.list_url = reverse("products-list")
        self.detail_url = reverse(
            "products-detail", kwargs={"slug": self.active_product.slug}
        )

        # Reusable payload
        self.create_payload = {
            "name": "New",
            "description": "New",
            "brand": self.brand.pk,
            "category": self.category.pk,
        }

    # Read tests
    def test_query_count(self):
        self.client.force_authenticate(self.staff)

        # Or use `with CaptureQueriesContext(connection) as ctx`
        # Total count from PageNumberPagination, products, prefetched variants, prefetched images
        with self.assertNumQueries(4):
            self.client.get(self.list_url)

    def test_public_sees_only_active_products(self):
        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]

        self.assertIn(self.active_product.name, names)
        self.assertNotIn(self.inactive_product.name, names)

    def test_public_sees_only_active_variants_and_images(self):
        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        variants = item.get("variants", [])
        if variants:
            self.assertEqual(len(variants), 1)
            self.assertEqual(len(variants[0]["images"]), 1)

    def test_staff_sees_all_variants_and_images(self):
        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        variants = item.get("variants", [])
        if variants:
            self.assertEqual(len(variants), 2)
            self.assertEqual(len(variants[0]["images"]), 2)

    def test_staff_sees_all_products(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]

        self.assertIn(self.active_product.name, names)
        self.assertIn(self.inactive_product.name, names)

    def test_variants_count_is_correct(self):
        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        self.assertEqual(item["variants_count"], 1)  # only active

    def test_list_uses_list_serializer_shape(self):
        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("variants_count", item)
        self.assertNotIn("variants", item)

    def test_detail_uses_detail_serializer_shape(self):
        response = self.client.get(self.detail_url)
        item = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("variants", item)
        self.assertIn("description", item)

    def test_public_does_not_see_is_active_field(self):
        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        self.assertNotIn("is_active", item)

    def test_staff_sees_is_active_field(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(self.list_url)
        item = response.data["results"][0]

        self.assertIn("is_active", item)

    def test_category_filter_includes_descendants_products(self):
        root = Category.add_root(name="Root")
        child = root.add_child(name="Child")
        grandchild = child.add_child(name="Grandchild")
        product_a = Product.objects.create(
            name="A",
            description="A",
            brand=self.brand,
            category=root,
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

        response = self.client.get(self.list_url, {"category": root.slug})
        names = [p["name"] for p in response.data["results"]]

        self.assertIn(product_a.name, names)
        self.assertIn(product_b.name, names)
        self.assertIn(product_c.name, names)

    def test_category_filter_excludes_parent_products(self):
        root = Category.add_root(name="root")
        child = root.add_child(name="child")
        product_a = Product.objects.create(
            name="A",
            description="A",
            brand=self.brand,
            category=root,
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
        category = Category.add_root(name="A")
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
    def test_non_staff_cannot_create_product(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_product(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_create_returns_detail_serializer(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertIn("slug", response.data)
        self.assertIn("brand", response.data)
        self.assertIn("category", response.data)


class VariantViewSetTest(APITestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

        # Related objects
        self.brand = Brand.objects.create(name="Brand")
        self.category = Category.add_root(name="Category")
        self.product = Product.objects.create(
            name="Product",
            description="Product",
            brand=self.brand,
            category=self.category,
        )

        # Variants
        self.active_variant = Variant.objects.create(
            sku="sku-active",
            product=self.product,
            is_active=True,
        )
        self.inactive_variant = Variant.objects.create(
            sku="sku-inactive",
            product=self.product,
            is_active=False,
        )

        # Variant images
        self.active_img = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            is_active=True,
            variant=self.active_variant,
        )
        self.inactive_img = VariantImage.objects.create(
            image=create_test_image(),
            order=2,
            is_active=False,
            variant=self.active_variant,
        )

        # URLs
        self.list_url = reverse("variants-list")
        self.detail_url = reverse(
            "variants-detail", kwargs={"uuid": self.active_variant.uuid}
        )

        # Reusable payload
        self.create_payload = {
            "sku": "sku-new",
            "product": self.product.pk,
        }

    # Read tests
    def test_query_count(self):
        self.client.force_authenticate(self.staff)

        # Total count from PageNumberPagination, variants, prefetched images
        with self.assertNumQueries(3):
            self.client.get(self.list_url)

    def test_public_cannot_see_variant_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_sees_all_variants(self):
        self.client.force_authenticate(self.staff)

        response = self.client.get(self.list_url)
        codes = [v["sku"] for v in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.active_variant.sku, codes)
        self.assertIn(self.inactive_variant.sku, codes)

    def test_public_does_not_see_is_active_field(self):
        response = self.client.get(self.detail_url)
        item = response.data

        self.assertIn("uuid", item)
        self.assertNotIn("is_active", item)

    def test_staff_sees_is_active_field(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(self.detail_url)
        item = response.data

        self.assertIn("is_active", item)

    # Write tests
    def test_non_staff_cannot_create_variant(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_variant(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Variant.objects.count(), 3)


class VariantImageViewSetTest(APITestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass",
            is_staff=False,
        )

        # Related objects
        self.brand = Brand.objects.create(name="Brand")
        self.category = Category.add_root(name="Category")
        self.product = Product.objects.create(
            name="Product",
            description="Product",
            brand=self.brand,
            category=self.category,
        )
        self.variant = Variant.objects.create(
            sku="sku-1",
            product=self.product,
        )

        # Variant images
        self.active_img = VariantImage.objects.create(
            image=create_test_image(),
            order=1,
            is_active=True,
            variant=self.variant,
        )
        self.inactive_img = VariantImage.objects.create(
            image=create_test_image(),
            order=2,
            is_active=False,
            variant=self.variant,
        )

        # URLs
        self.list_url = reverse("variant-images-list")
        self.detail_url = reverse(
            "variant-images-detail", kwargs={"uuid": self.active_img.uuid}
        )

        # Reusable payload
        self.create_payload = {
            "image": create_test_image(),
            "alt_text": "New",
            "order": 3,
            "variant": self.variant.pk,
        }

    # Read tests
    def test_query_count(self):
        self.client.force_authenticate(self.staff)

        # Total count from PageNumberPagination, variant images
        with self.assertNumQueries(2):
            self.client.get(self.list_url)

    def test_public_cannot_see_image_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_sees_all_images(self):
        self.client.force_authenticate(self.staff)

        response = self.client.get(self.list_url)
        codes = [i["uuid"] for i in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.active_img.uuid), codes)
        self.assertIn(str(self.inactive_img.uuid), codes)

    def test_public_does_not_see_is_active_field(self):
        response = self.client.get(self.detail_url)
        item = response.data

        self.assertIn("uuid", item)
        self.assertNotIn("is_active", item)

    def test_staff_sees_is_active_field(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(self.detail_url)
        item = response.data

        self.assertIn("is_active", item)

    # Write tests
    def test_non_staff_cannot_create_image(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_image(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VariantImage.objects.count(), 3)

    def test_create_returns_detail_serializer(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(self.list_url, self.create_payload)

        self.assertIn("variant_uuid", response.data)
        self.assertIn("variant_sku", response.data)
