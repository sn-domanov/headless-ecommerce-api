from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.products.api.v1 import views

# TODO consider switching to SimpleRouter when Api Root view is not needed anymore
router = DefaultRouter()
router.register("brands", views.BrandViewSet, basename="brands")
router.register("categories", views.CategoryViewSet, basename="categories")
router.register("products", views.ProductViewSet, basename="products")
router.register("variants", views.VariantViewSet, basename="variants")
router.register("variant-images", views.VariantImageViewSet, basename="variant-images")

urlpatterns = [
    path("", include(router.urls)),
]
