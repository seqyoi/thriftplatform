from django.core.management.base import BaseCommand
import pandas as pd
from thrifty.models import Category  # use your app name

df = pd.read_csv('path/to/file.csv')

# Assume the column is named 'category' or similar
for name in df['category'].dropna().unique():
    Category.objects.get_or_create(name=name)
