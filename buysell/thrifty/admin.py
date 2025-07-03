from django.contrib import admin
from .models import PasswordReset
from .models import Product, Review


# thrifty/admin.py
from .models import Category, CategoryImage

admin.site.register(Category)
admin.site.register(PasswordReset)
admin.site.register(CategoryImage)
# Register your models here.
admin.site.register(Product)
admin.site.register(Review)