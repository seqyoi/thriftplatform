from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from thrifty import views
from .views import chatbot_ui, chatbot_reply

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
    
    # path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('chat/', views.chatbot_ui, name='chat-ui'),
    path('chatbot/reply/', views.chatbot_reply, name='chatbot-reply'),
    path('search/', views.search_products, name='search'),  # i have added search here inside the main list
    path('upload/', views.upload_product, name='upload_product'),
   path('profile/<str:username>/edit/<int:product_id>/', views.edit_product, name='edit_product'),
   path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
   path('user/<str:username>/', views.profile, name='profile'),
    path('reviews/add/<str:model_name>/<int:object_id>/', views.add_review, name='add_review'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



