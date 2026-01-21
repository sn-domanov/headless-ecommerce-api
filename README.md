# headless-ecommerce-api
Headless e-commerce backend built with Django REST Framework

## Running locally
Default settings: `DJANGO_SETTINGS_MODULE=config.settings.dev`
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```