# Headless E-commerce API

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

## JWT Authentication

This project uses [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) for JWT-based authentication.

**Endpoints:**

| Path                 | Method | Purpose                                  |
|----------------------|--------|------------------------------------------|
| `/api/token/`        | POST   | Obtain access and refresh tokens         |
| `/api/token/refresh/`| POST   | Refresh access token using refresh token |

### Obtain tokens

```http
POST /api/token/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Qq12345678"
}
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

### Refresh access token

Refresh tokens are rotated and blacklisted each time the `/api/token/refresh/` endpoint is called. Each refresh request returns:
- a new access token
- a new refresh token

Add a cron job `python manage.py flushexpiredtokens` to remove expired OutstandingTokens and BlacklistedTokens, preventing the token tables from growing indefinitely.

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<your refresh token here>"
}
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

### Testing with REST Client

All JWT endpoints can be tested via the included `http/auth.http` file with the [VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client).
