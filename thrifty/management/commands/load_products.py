import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
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

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        try:
            df = pd.read_csv(csv_path)
            self.stdout.write(f"✅ Loaded CSV with {len(df)} rows")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to read CSV: {str(e)}"))
            return

        df.columns = df.columns.str.strip()
        required_cols = {'product_id', 'product_name'}

        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            self.stdout.write(self.style.ERROR(f"❌ Missing columns: {', '.join(missing)}"))
            return

        # Drop rows missing essential fields
        df = df.dropna(subset=['product_id', 'product_name'])

        # ✅ Cast product_id to string and strip whitespace (critical for your use case)
        df['product_id'] = df['product_id'].astype(str).str.strip()

        # Get system user to assign as uploader for CSV products
        try:
            system_user = User.objects.get(username='thriftify_admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ 'thriftify_admin' user does not exist. Please create it first."))
            return

        created_count = 0
        for _, row in df.iterrows():
            image_url = f"category_images/{row['imagefilename']}" if 'imagefilename' in row and pd.notna(row['imagefilename']) else ''
            
            # Convert price safely
            price = None
            if 'price' in row and pd.notna(row['price']):
                try:
                    price = float(row['price'])
                except (ValueError, TypeError):
                    price = None

            # Clean category and description fields
            category = row.get('category', '')
            if pd.isna(category):
                category = ''

            description = row.get('description', '')
            if pd.isna(description):
                description = ''

            # Create or update Product using string product_id
            _, created = Product.objects.update_or_create(
                product_id=row['product_id'],
                defaults={
                    'name': row['product_name'],
                    'category': category,
                    'description': description,
                    'image_url': image_url,
                    'rating': float(row.get('rating')) if 'rating' in row and pd.notna(row['rating']) else None,
                    'price': price,
                    'user': system_user,  # Assign uploader
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Success! Created {created_count} new products"))
