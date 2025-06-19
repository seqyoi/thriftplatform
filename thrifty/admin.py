from django.contrib import admin
from .models import PasswordReset
from .models import Category
from .models import Product
from .models import ProductView
from .models import Category, CategoryImage
from django.utils.html import format_html


admin.site.register(PasswordReset)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductView)

class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height:auto;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

admin.site.register(CategoryImage, CategoryImageAdmin)

# Register your models here.
