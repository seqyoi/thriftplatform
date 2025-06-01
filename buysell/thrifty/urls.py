from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from thrifty import views

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path("register/",views.register, name= 'register'),
     path('', views.home, name='home'),
     path('logout/', views.logout_view, name='logout'),
     path('shop/',views.shop_view, name='shop'),
     path('forgot-password/',views.forgotpassword, name='forgot-password'),
     path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('category_list/',views.category_list,name='category_list' ),
     path('category/<int:pk>/', views.category_detail, name='category_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


