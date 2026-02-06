from datetime import timedelta

from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

access_lifetime: timedelta = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
refresh_lifetime: timedelta = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

access_max_age = int(access_lifetime.total_seconds())
refresh_max_age = int(refresh_lifetime.total_seconds())


class CookieTokenCreateView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        response.set_cookie(
            "access_token",
            access,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            # Set session cookie lifetime to JWT token lifetime
            max_age=access_max_age,
        )
        response.set_cookie(
            "refresh_token",
            refresh,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=refresh_max_age,
        )

        # Only pass JWT in cookies, but might be carefully relaxed if needed
        response.data = {"detail": "Login successful"}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return Response({"detail": "Refresh token missing or invalid"}, status=401)

        request.data["refresh"] = refresh
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh_new = response.data.get("refresh")

        response.set_cookie(
            "access_token",
            access,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=access_max_age,
        )

        response.set_cookie(
            "refresh_token",
            refresh_new,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=refresh_max_age,
        )

        response.data = {"detail": "Token refreshed"}
        return response


class CookieTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        token = request.COOKIES.get("access_token")
        if not token:
            return Response({"detail": "No access token"}, status=401)
        try:
            AccessToken(token)  # pyright: ignore[reportArgumentType]
            return Response({"detail": "Token valid"}, status=200)
        except TokenError as e:
            return Response({"detail": str(e)}, status=401)


class LogoutView(APIView):
    # Allow anyone to hit logout to make it idempotent.
    permission_classes = [AllowAny]

    def post(self, request: Request):
        refresh = request.COOKIES.get("refresh_token")
        if refresh:
            try:
                token = RefreshToken(refresh)  # pyright: ignore[reportArgumentType]
                token.blacklist()
            # Logout should never fail
            except TokenError:
                pass  # already invalid / expired / blacklisted

        response = Response(status=204)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
