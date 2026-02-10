# Ecommerce API

Headless e-commerce backend built with Django REST Framework.

## Requirements

- Python 3.13+

Dependencies are managed using pip and are listed in `requirements/`.

## Environment variables

Copy `.env.template` to `.env`:

```sh
cp .env.template .env
```

Generate a secret key for development:

```sh
python -c "from django.core.management.utils import get_random_secret_key(); print(get_random_secret_key())"
```

Edit `.env` and replace `SECRET_KEY` with the generated key (use single quotes).

## Running locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at:
http://127.0.0.1:8000/

## Running tests

Tests are run using pytest:

```sh
pytest
```

## Settings

The project uses environment-specific settings:
- `config.settings.dev` – local development
- `config.settings.test` – automated tests

The default settings module is `config.settings.dev`.

## Admin panel

The Django admin panel is available at:
http://127.0.0.1:8000/admin/

## Authentication

This project uses [Djoser](https://djoser.readthedocs.io/) for user management and
[SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) for JWT-based authentication.

**Cookie-based JWT**: Access and refresh tokens are stored in **HttpOnly cookies**.  
This prevents JavaScript from reading tokens directly, improving security.

Users created via the API are inactive by default. An activation link is emailed to the user after signup.

**Endpoints:**

| Path                                          | Method | Purpose                                               |
|-----------------------------------------------|--------|-------------------------------------------------------|
| `/api/auth/jwt/create/`                       | POST   | Obtain access and refresh tokens                      |
| `/api/auth/jwt/refresh/`                      | POST   | Refresh access token                                  |
| `/api/auth/jwt/verify/`                       | POST   | Verify access token                                   |
| `/api/auth/jwt/logout/`                       | POST   | Logout user (delete cookies, blacklist refresh token) |
| `/api/auth/users/activation/`                 | POST   | Activate a user account                               |
| `/api/auth/users/resend_activation/`          | POST   | Re-send activation email                              |
| `/api/auth/users/`                            | POST   | Create user (signup)                                  |
| `/api/auth/users/me/`                         | GET    | Get current authenticated user                        |
| `/api/auth/users/reset_password/`             | POST   | Request password reset email                          |
| `/api/auth/users/reset_password_confirm/`     | POST   | Confirm password reset                                |


For all user-related endpoints see [Djoser docs](https://djoser.readthedocs.io/en/latest/getting_started.html)

### Create user (signup)

```http
POST /api/auth/users/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "Qq12345678",
    "re_password": "Qq12345678"
}
```

Response:

```json
{
  "email": "user@example.com",
  "id": 2
}
```

After creating a user, check the console email output.
The activation link looks like:
`/activate/<uid>/<token>/`

Use `<uid>` and `<token>` (remove the line break and the trailing `=` character) in user activation request.

### Activate user

```http
POST /api/auth/users/activation/
Content-Type: application/json

{
    "uid": "2",
    "token": "user_activation_token"
}
```

Response:

Returns HTTP 204 on success.

### Resend user activation email

Note that no email would be sent if the user is already active or if they don’t have a usable password.

```http
POST /api/auth/users/resend_activation/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Response:

Returns HTTP 204 on success.

After requesting activation link, check the console email output.
The activation link looks like:
`/activate/<uid>/<token>/`

Use `<uid>` and `<token>` (remove the line break and the trailing `=` character) in user activation request.

### Obtain tokens

```http
POST /api/auth/jwt/create/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Qq12345678"
}
```

Response:

```json
{
  "detail": "Login successful"
}
```

Tokens are set as HttpOnly cookies: access_token and refresh_token.

### Refresh access token

Refresh tokens are rotated and blacklisted each time the `/api/auth/jwt/refresh/` endpoint is called.

Add a cron job `python manage.py flushexpiredtokens` to remove expired OutstandingTokens and BlacklistedTokens, preventing the token tables from growing indefinitely.

```http
POST /api/auth/jwt/refresh/
Content-Type: application/json
# Cookie-based, no body needed
```

Response:

```json
{
  "detail": "Token refreshed"
}
```

Tokens are set as HttpOnly cookies: access_token and refresh_token.

### Verify access token

```http
POST /api/auth/jwt/verify/
Content-Type: application/json
# Cookie-based, no body needed
```

Response:

```json
{
  "detail": "Token valid"
}
```

Returns 401 if the token is missing or invalid.

## Logout

```http
POST /api/auth/jwt/logout/
Content-Type: application/json
# Cookie-based, no body needed; idempotent
```

- Deletes access_token and refresh_token cookies
- Blacklists the refresh token
- Idempotent: calling logout multiple times is safe
- Returns HTTP 204 on success

### Get current user

```http
GET /api/auth/users/me/
# Cookie-based, no Authorization header needed
```

Response:

```json
{
  "id": 2,
  "email": "user@example.com"
}
```

### Request password reset email

```http
POST /api/auth/users/reset_password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Response:

Returns HTTP 204 on success.

After requesting a password reset, check the console email output.
The reset link looks like:
`/reset-password/<uid>/<token>/`

Use `<uid>` and `<token>` (remove the line break and the trailing `=` character) in password reset confirmation request.

### Confirm password reset

```http
POST /api/auth/users/reset_password_confirm/
Content-Type: application/json

{
  "uid": "<uid>",
  "token": "<token>",
  "new_password": "NewStrongPassword123!",
  "re_new_password": "NewStrongPassword123!"
}
```

Response:

Returns HTTP 204 on success.

### Testing with REST Client

All JWT endpoints can be tested via the included `http/auth.http` file with the [VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client). The file uses variables that must be filled manually (email, passwords, UID, reset token).
