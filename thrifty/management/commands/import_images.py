import os
from django.core.management.base import BaseCommand
from django.core.files import File
from thrifty.models import Category, CategoryImage

class Command(BaseCommand):
    help = 'Import category images from subfolders inside category_images'

    def handle(self, *args, **kwargs):
        base_folder = os.path.join(os.getcwd(), 'category_images')

        if not os.path.exists(base_folder):
            self.stdout.write(self.style.ERROR(f"Folder {base_folder} does not exist."))
            return

        for category_name in os.listdir(base_folder):
            category_path = os.path.join(base_folder, category_name)
            if os.path.isdir(category_path):
                category, created = Category.objects.get_or_create(name=category_name)
                self.stdout.write(f"Processing category: {category_name}")
                for filename in os.listdir(category_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png']:
                        filepath = os.path.join(category_path, filename)
                        with open(filepath, 'rb') as f:
                            img = CategoryImage(category=category)
                            img.image.save(filename, File(f), save=True)
                        self.stdout.write(f"  Imported image: {filename}")
        self.stdout.write(self.style.SUCCESS('Import complete!'))
