import uuid6
from autoslug import AutoSlugField
from django.db import models


def product_thumbnail_upload_path(instance, filename) -> str:
    return f"products/{instance.uuid}/thumbnails/product/{filename}"


def variant_image_upload_path(instance, filename) -> str:
    # `variant_id` is chosen over `variant.sku` because SKU might change
    return f"products/{instance.variant.product.uuid}/images/variants/{instance.variant.uuid}/{filename}"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", unique=True)
    # Using adjacency list for MVP. Can be replaced with MPTT (currently unmaintained) or treebeard.
    parent = models.ForeignKey(
        to="self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)

    # TODO switch to django-treebeard
    def get_descendants(self, include_self: bool) -> list:
        descendants = [self] if include_self else []

        children = list(self.children.all())
        descendants.extend(self.children.all())

        for child in children:
            descendants.extend(child.get_descendants(include_self=False))
        return descendants


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Product(models.Model):
    category = models.ForeignKey(
        to=Category, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(
        to=Brand, on_delete=models.CASCADE, related_name="products"
    )
    # Keeping BigAutoField PK for now
    uuid = models.UUIDField(default=uuid6.uuid7, editable=False, unique=True)
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to=product_thumbnail_upload_path, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usage: Product.objects.active()
    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["brand", "is_active"]),
        ]

    def __str__(self) -> str:
        return str(self.name)


class VariantQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, product__is_active=True)


class Variant(models.Model):
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name="variants"
    )
    uuid = models.UUIDField(default=uuid6.uuid7, editable=False, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VariantQuerySet.as_manager()

    class Meta:
        # Lexicographical order, consider if SKU is numeric-like (not this project)
        ordering = ["sku"]
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.sku}"

    @property
    def primary_image(self):
        return self.images.active().order_by("order", "id").first()


class VariantImageQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class VariantImage(models.Model):
    variant = models.ForeignKey(
        to=Variant, on_delete=models.CASCADE, related_name="images"
    )
    uuid = models.UUIDField(default=uuid6.uuid7, editable=False, unique=True)
    image = models.ImageField(upload_to=variant_image_upload_path, max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VariantImageQuerySet.as_manager()

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["variant", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"Image for variant: {self.variant.sku} #{self.order}"
