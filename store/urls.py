from django.contrib import admin
from django.urls import path, include
from store import views
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name="home"),
    path('shop', views.shop, name="shop"),
    path('cart/', views.cart, name='cart'),
    path('get-cart-items/', views.get_cart_items, name='get-cart-items'),
    path('checkout', views.checkout, name="checkout"),
    path('contact', views.contact, name="contact"),
    path('prod_view/<int:sno>/', views.prod_view, name="prod_view"),
    path('user_acc', views.user_account, name="user_account"),
    path('order_history', views.order_history, name="order_history"),
    path('prod_view/<int:sno>/submit_review/', views.submit_review, name="submit_review"),
    path('login', views.user_login, name="login"),
    path('signup', views.signup, name="signup"),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)