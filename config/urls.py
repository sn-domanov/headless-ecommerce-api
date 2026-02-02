"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import IsAuthenticated

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth (Djoser + JWT)
    re_path(r"^api/auth/", include("djoser.urls")),
    re_path(r"^api/auth/", include("djoser.urls.jwt")),
    # Products
    path("api/v1/", include("apps.products.api.v1.urls.public")),
    path("api/v1/admin/", include("apps.products.api.v1.urls.admin")),
    # Swagger
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(custom_settings={"VERSION": "1.0.0"}),
        name="schema_v1",
    ),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema_v1", permission_classes=[IsAuthenticated]
        ),
    ),
]
