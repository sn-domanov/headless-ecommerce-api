# headless-ecommerce-api
Headless e-commerce backend built with Django REST Framework

## Running locally
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

## Settings
The project uses environment-specific settings:
- `config.settings.dev` – local development (default)
- `config.settings.test` – automated tests
The default settings module is `config.settings.dev`.