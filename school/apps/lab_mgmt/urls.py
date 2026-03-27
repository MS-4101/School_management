from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    path('labs/', views.lab_list, name='lab_list'),
    path('labs/create/', views.lab_create, name='lab_create'),
    path('labs/<int:pk>/edit/', views.lab_edit, name='lab_edit'),
    path('labs/<int:pk>/delete/', views.lab_delete, name='lab_delete'),
    path('categories/', views.eq_category_list, name='eq_category_list'),
    path('categories/create/', views.eq_category_create, name='eq_category_create'),
    path('categories/<int:pk>/edit/', views.eq_category_edit, name='eq_category_edit'),
    path('categories/<int:pk>/delete/', views.eq_category_delete, name='eq_category_delete'),
    path('subcategories/', views.eq_subcategory_list, name='eq_subcategory_list'),
    path('subcategories/create/', views.eq_subcategory_create, name='eq_subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.eq_subcategory_edit, name='eq_subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.eq_subcategory_delete, name='eq_subcategory_delete'),
    path('api/subcategories/', views.ajax_eq_subcategories, name='ajax_eq_subcategories'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/approve/', views.booking_approve, name='booking_approve'),
    path('bookings/<int:pk>/return/', views.booking_return, name='booking_return'),
]
