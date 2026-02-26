from typing import Optional

import requests
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.products.models import Brand, Category, Product


class Command(BaseCommand):
    help = "Seed products from DummyJSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Number of products to import",
        )
        parser.add_argument(
            "--skip",
            type=int,
            default=0,
            help="Number of products to skip",
        )
        parser.add_argument(
            "--download-images",
            action="store_true",
            help="Download and store product images locally",
        )

    def download_file(self, url: str) -> Optional[ContentFile]:
        try:
            r = requests.get(url, timeout=(5, 10))
            r.raise_for_status()
            return ContentFile(r.content)
        except requests.RequestException as e:
            self.stderr.write(f"Failed to fetch {url}: {e}")
            return None

    def handle(self, *args, **options):
        limit = options["limit"]
        skip = options["skip"]
        source_url = f"https://dummyjson.com/products?limit={limit}&skip={skip}"
        download_images = options["download_images"]

        if not Category.objects.exists():
            self.stdout.write("Loading categories fixture")
            call_command("loaddata", "apps/products/fixtures/category.json")

        # Fetch products from DummyJSON
        self.stdout.write(f"Fetching products from {source_url}")
        try:
            res = requests.get(source_url, timeout=(5, 10))
            res.raise_for_status()
        except requests.RequestException as e:
            self.stderr.write(f"Failed to fetch {source_url}: {e}")
            return

        data = res.json()
        products = data.get("products")
        if not products:
            self.stderr.write("No products found in response")
            return

        for product in products:
            # Category
            category_slug = product.get("category")
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                self.stderr.write(f"Couldn't find category with slug {category_slug}")
                continue

            # Brand
            brand_name = product.get("brand", "No brand")
            brand, _ = Brand.objects.get_or_create(name=brand_name)

            # Product
            product_obj, product_created = Product.objects.get_or_create(
                name=product["title"],
                defaults={
                    "category": category,
                    "brand": brand,
                    "description": product["description"],
                    "is_digital": False,
                },
            )

            # Thumbnail
            thumbnail_url = product.get("thumbnail")
            # Download for newly created objects only
            if download_images and product_created and thumbnail_url:
                file = self.download_file(thumbnail_url)
                if file:
                    product_obj.thumbnail.save(
                        f"{product_obj.slug}.webp",
                        file,
                        save=True,
                    )

            # Product images
            images_list = product.get("images")
            if download_images and product_created and images_list:
                for idx, url in enumerate(images_list):
                    file = self.download_file(url)
                    if file:
                        image_obj = product_obj.images.create()
                        image_obj.image.save(
                            f"{product_obj.slug}-{idx}.webp",
                            file,
                            save=True,
                        )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
