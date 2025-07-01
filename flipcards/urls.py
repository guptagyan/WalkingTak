from django.urls import path
from django.contrib.auth import views as auth_views
from cards import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
app_name = 'store'

urlpatterns = [
    # Home page
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('order/success/', views.order_success, name='order_success'),
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    # path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Changed from 'cart_add'
    # path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('orders/', views.order_history, name='order_history'),
    path('checkout/', views.checkout, name='checkout'),

    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


    path('faq/', views.faq, name='faq'),
    path('track-order/', views.track_order, name='track_order'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    
   
   
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
