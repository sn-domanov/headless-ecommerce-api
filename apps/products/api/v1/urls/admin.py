from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.products.api.v1 import views

# TODO consider switching to SimpleRouter when browsable API is not needed anymore
router = DefaultRouter()
# Queryset is retrieved using a method (not a class attribute), so basename must be set explicitly
router.register("products", views.ProductAdminViewSet, basename="admin-products")

urlpatterns = [
    path("", include(router.urls)),
]
