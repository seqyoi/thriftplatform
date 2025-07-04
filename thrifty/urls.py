from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from thrifty import views
from .views import chatbot_ui, chatbot_reply
from django.contrib.auth import views as auth_views
from uuid import UUID 

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path("register/",views.register, name= 'register'),
    path('', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('shop/',views.shop_view, name='shop'),
    
     path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('category/<str:category_name>/', views.category_view, name='category_view'),
    path('category-api/<str:category_name>/', views.category_partial, name='category_partial'),


    
    # path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('product/id/<int:id>/', views.product_redirect_by_id, name='product_redirect_by_id'),

    path('chat/', views.chatbot_ui, name='chat-ui'),
    path('chatbot/reply/', views.chatbot_reply, name='chatbot-reply'),
    path('search/', views.search_products, name='search'),  # i have added search here inside the main list
    path('upload/', views.upload_product, name='upload_product'),
   path('profile/<str:username>/edit/<int:product_id>/', views.edit_product, name='edit_product'),
   path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
   path('user/<str:username>/', views.profile, name='profile'),
    path('reviews/add/<str:model_name>/<int:object_id>/', views.add_review, name='add_review'),
path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



