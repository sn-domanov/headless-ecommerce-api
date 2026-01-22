from django.contrib import admin

from apps.products.models import Brand, Category, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["category", "brand", "name", "is_active", "is_digital"]
    list_filter = ["is_active", "is_digital", "category", "brand"]
    search_fields = ["name", "description"]
