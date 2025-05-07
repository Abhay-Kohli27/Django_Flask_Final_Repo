from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landingpage'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('userprofile/', views.user_profile_view, name='userprofile'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('contact_us', views.contact_view, name='contact')
]