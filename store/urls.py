from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
app_name = 'store'

urlpatterns = [
    path('',views.home, name="home"),
    path('product/', views.product, name='product'),
    
    path('product_list/<int:category_id>/', views.product_list, name='product_list'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path("cart-items-json/", views.cart_items_json, name="cart_items_json"),
     path("update-cart-ajax/<int:variant_id>/", views.update_cart_ajax, name="update_cart_ajax"),
      path("remove-from-cart-ajax/<int:variant_id>/", views.remove_from_cart_ajax, name="remove_from_cart_ajax"),
    path('add-to-cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('success/', views.success, name='success'),
    path("checkout/", views.checkout, name="checkout"),
    path('get-delivery-charge/', views.get_delivery_charge, name='get_delivery_charge'),
    
    
]

