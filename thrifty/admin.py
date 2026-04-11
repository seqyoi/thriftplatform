from django.contrib import admin
from .models import PasswordReset
from .models import Category
from .models import Product
from .models import ProductView
from .models import Category, CategoryImage
from django.utils.html import format_html
from .models import Review
from .models import Order
from .models import OrderItem
from .models import Post
from .models import CartItem
from .models import Profile


admin.site.register(Product)

admin.site.register(Review)

admin.site.register(Profile)

class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height:auto;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

admin.site.register(CategoryImage, CategoryImageAdmin)

# Register your models here.
from django.contrib import admin
from .models import Order, OrderItem, Product

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No empty rows by default

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'receiver_name', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)