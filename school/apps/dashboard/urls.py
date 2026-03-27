from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.home, name='home'),
    path('dashboard/school/', views.school_dashboard, name='school_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
]
