from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class Category(models.Model):
    name = models.CharField(max_length=255)
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
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_per_parent",
            )
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


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
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usage: Product.objects.active()
    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.name)
