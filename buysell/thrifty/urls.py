from django.contrib import admin
from django.urls import path

from thrifty import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login_view, name='login'),
    path("register/",views.register, name= 'register'),
     path('', views.home, name='home'),
     path('logout/', views.logout_view, name='logout'),
     path('product1/',views.shop_view, name='shop')  
]
