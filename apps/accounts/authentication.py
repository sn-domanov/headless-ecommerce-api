from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


def enforce_csrf(request):
    check = CsrfViewMiddleware(lambda req: None)  # pyright: ignore[reportArgumentType]
    check.process_request(request)
    reason = check.process_view(
        request, None, (), {}  # pyright: ignore[reportArgumentType]
    )
    if reason:
        raise PermissionDenied(f"CSRF Failed: {reason}")


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))

        # N.B. this enforces CSRF for authenticated users only (login doesn't enforce CSRF)
        enforce_csrf(request)

        return self.get_user(validated_token), validated_token
