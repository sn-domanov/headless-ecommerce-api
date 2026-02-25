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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import IsAuthenticated

from apps.accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Secure HttpOnly cookie JWT auth
    path("api/auth/jwt/create/", accounts_views.CookieTokenCreateView.as_view()),
    path("api/auth/jwt/refresh/", accounts_views.CookieTokenRefreshView.as_view()),
    path("api/auth/jwt/verify/", accounts_views.CookieTokenVerifyView.as_view()),
    path("api/auth/jwt/logout/", accounts_views.LogoutView.as_view()),
    # Djoser + JWT: registration, activation, password reset
    re_path(r"^api/auth/", include("djoser.urls")),
    # Products
    path("api/v1/", include("apps.products.api.v1.urls")),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
