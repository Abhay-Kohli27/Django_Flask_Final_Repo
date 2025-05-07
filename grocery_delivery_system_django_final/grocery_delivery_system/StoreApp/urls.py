from django.urls import path
from . import views

urlpatterns = [
    path('manage/<int:store_id>/',views.manage_store_view, name = 'store_manage'),
    path('add_product/<int:store_id>/', views.add_product_view, name='add_product'),
    path('add_store/', views.add_store_view, name='add_store'),
    path('store/<int:store_id>/', views.view_store, name='store'),
    path('store/update/', views.update_store, name='update_store'),
]