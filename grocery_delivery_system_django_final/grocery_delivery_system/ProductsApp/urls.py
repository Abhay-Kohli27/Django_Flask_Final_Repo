from django.urls import path
from . import views

urlpatterns = [
    path("", views.show_products_view, name="products"),
    path('product/<int:product_id>',views.show_individual_product,name="show_individual_product"),
    path('delete_product/<int:product_id>', views.delete_product, name='delete_product'),
    path('update_product/<int:product_id>', views.update_product, name='update_product'),
    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
]