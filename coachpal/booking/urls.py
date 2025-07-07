from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 
from django.contrib.auth.views import LoginView
from . import views
from django.views.decorators.http import require_http_methods

app_name = 'booking'
urlpatterns = [
    path('', views.acceuil, name='acceuil'),
    path('book/', views.book_appointment, name='form'),
    path('success/', views.success, name='success'),

    # Auth
    path('accounts/login/', LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('accounts/logout/', require_http_methods(["POST"])(views.custom_logout), name='logout'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),  # mot de passe, reset etc.
    
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard_coach/', views.dashboard_coach, name='dashboard_coach'),
    path('dashboard_client/', views.dashboard_client, name='dashboard_client'),
]