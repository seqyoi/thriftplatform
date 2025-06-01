from django.contrib import admin
from .models import PasswordReset

admin.site.register(PasswordReset)
# thrifty/admin.py
from .models import Category

admin.site.register(Category)


# Register your models here.
