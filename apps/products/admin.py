from django.contrib import admin
from django.utils.html import format_html
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)

from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)


class VariantImageInline(NestedTabularInline):
    model = VariantImage
    extra = 1


class VariantInline(NestedStackedInline):
    model = Variant
    inlines = [VariantImageInline]
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    list_display = (
        "thumbnail_preview",
        "name",
        "slug",
        "category",
        "brand",
        "is_active",
    )
    list_display_links = ("name",)
    list_filter = ("is_active", "category", "brand")
    search_fields = ("name", "description")
    inlines = (VariantInline,)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html("<img src={} style='height:40px;' />", obj.thumbnail.url)
        return "—"

    thumbnail_preview.short_description = "Thumbnail"
