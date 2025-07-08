import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buysell.settings')  
django.setup()

from django.core.files import File
from thrifty.models import Category, CategoryImage  

IMAGE_FOLDER = 'media/category_images/'  # Where your images are stored

for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        # Get the name without extension, e.g., 'electronics' from 'electronics.jpg'
        category_name = os.path.splitext(filename)[0]

        # Try to find the category in DB matching this name (case-insensitive)
        try:
            category = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            print(f"Category '{category_name}' not found. Skipping {filename}.")
            continue

        # Add the image to the CategoryImage table linked to the found category
        image_path = os.path.join(IMAGE_FOLDER, filename)
        with open(image_path, 'rb') as f:
            image_file = File(f)

            # Avoid duplicates: check if image already exists for this category
            if not CategoryImage.objects.filter(category=category, image=f"category_images/{filename}").exists():
                CategoryImage.objects.create(category=category, image=image_file)
                print(f"Imported {filename} for category {category.name}")
            else:
                print(f"Image {filename} already exists for category {category.name}")
