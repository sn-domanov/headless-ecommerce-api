# Headless E-commerce API

Headless e-commerce backend built with Django REST Framework.

## Requirements

- Python 3.12+

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
