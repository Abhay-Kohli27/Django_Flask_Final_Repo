from django.urls import path
from . import views

urlpatterns = [
    path('add_to_cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('view_cart', views.view_cart, name='view_cart'),
    path('update_or_remove_cart_item/<int:item_id>', views.update_or_remove_cart_item, name='update_or_remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    
]