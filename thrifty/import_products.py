import csv
import os
from django.core.files import File
from django.conf import settings
from thrifty.models import Product, Category  

CSV_PATH = os.path.join(settings.BASE_DIR, 'category_product_data.csv')
IMAGE_DIR = os.path.join(settings.BASE_DIR, 'media/category_images')

def run():
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category, _ = Category.objects.get_or_create(name=row['category'])

            image_path = os.path.join(IMAGE_DIR, row['image_filename'])
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                continue

            with open(image_path, 'rb') as img_file:
                product = Product(
                    name=row['name'],
                    price=row['price'],
                    category=category,
                )
                product.image.save(os.path.basename(image_path), File(img_file), save=True)
                print(f"Imported: {product.name}")
