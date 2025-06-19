from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from thrifty import views

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path("register/",views.register, name= 'register'),
    path('', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('shop/',views.shop_view, name='shop'),
    path('forgot-password/',views.forgotpassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('category_list/',views.category_list,name='category_list' ),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('most_viewed/', views.most_viewed_products_view, name='most-viewed'),
    # path('popular/', views.popular_products_view, name='popular_products'),
    # path('recommend/<int:product_id>/', views.content_based_recommendations, name='content_recommendations'),
    # path('recommendations/', views.recommended_view, name='recommendations'),
    path('addtocart/<int:product_id>/', views.add_to_cart, name='add_to_cart')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


