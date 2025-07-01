import os
from django.conf import settings
from django.core.files import File
from thrifty.models import Product  # replace with your app name

def migrate_image_urls_to_image_files():
    count = 0
    products = Product.objects.filter(image_file__isnull=True).exclude(image_url='')

    for product in products:
        image_rel_path = product.image_url.strip('/')
        image_abs_path = os.path.join(settings.MEDIA_ROOT, image_rel_path)

        if os.path.exists(image_abs_path):
            with open(image_abs_path, 'rb') as f:
                filename = os.path.basename(image_abs_path)
                product.image_file.save(filename, File(f), save=True)
                product.image_url = ''  # clear old field
                product.save()
                print(f"Migrated: {product.name}")
                count += 1
        else:
            print(f"Missing file for: {product.name} → {image_abs_path}")

    print(f"✅ Migrated {count} products to image_file.")
