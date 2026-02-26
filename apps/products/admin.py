from django.contrib import admin
from django.utils.html import format_html

from apps.products.models import Brand, Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail_preview",
        "name",
        "slug",
        "category",
        "brand",
        "is_active",
        "is_digital",
    )
    list_display_links = ("name",)
    list_filter = ("is_active", "is_digital", "category", "brand")
    search_fields = ("name", "description")
    inlines = (ProductImageInline,)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html("<img src={} style='height:40px;' />", obj.thumbnail.url)
        return "—"

    thumbnail_preview.short_description = "Thumbnail"
