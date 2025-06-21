import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from thrifty.models import Product

class Command(BaseCommand):
    help = 'Load products from CSV into Product model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv_path',
            type=str,
            default=os.path.join(settings.BASE_DIR, 'thrifty', 'data', 'products.csv'),
            help='Custom path to CSV file'
        )

    def handle(self, *args, **options):  # Changed kwargs to options for consistency
        csv_path = options['csv_path']  # Changed kwargs to options

        # Verify CSV exists
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f"❌ File not found: {csv_path}")
            )
            return

        try:
            df = pd.read_csv(csv_path)
            self.stdout.write(f"✅ Loaded CSV with {len(df)} rows")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to read CSV: {str(e)}")
            )
            return

        # Clean and validate data
        df.columns = df.columns.str.strip()
        required_cols = {'product_id', 'product_name'}
        
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            self.stdout.write(
                self.style.ERROR(f"❌ Missing columns: {', '.join(missing)}")
            )
            return

        # Process data
        df = df.dropna(subset=['product_id', 'product_name'])
        df['product_id'] = df['product_id'].astype(str).str.strip()

        # Load products
        created_count = 0
        for _, row in df.iterrows():
            # image_url = ''
            # if 'imagefilename' in row and pd.notna(row['imagefilename']) and row['imagefilename'].strip() != '':
            #  image_url = f"media/category_images/{row['imagefilename'].strip()}"
            image_url = f"category_images/{row['imagefilename']}" if 'imagefilename' in row else ''
            print(row['imagefilename'])  # During loading
            price = None
            if 'price' in row and pd.notna(row['price']):
                        try:
                            price = float(row['price'])
                        except ValueError:
                            price = None     
            
            _, created = Product.objects.update_or_create(
                product_id=row['product_id'],
                defaults={
                    'name': row['product_name'],
                    'category': row.get('category', ''),
                    'description': row.get('description') if pd.notna(row.get('description')) else '',
                    'image_url': image_url,
                    'rating': float(row.get('rating')) if pd.notna(row.get('rating')) else None, 
                    'price': price,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Success! Created {created_count} new products")
        )