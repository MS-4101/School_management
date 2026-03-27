from django.urls import path
from . import views

app_name = 'buses'

urlpatterns = [
    # Bus Staff
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/start-trip/', views.start_trip, name='start_trip'),
    path('staff/trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('staff/pickup/<int:pickup_id>/mark/', views.mark_pickup, name='mark_pickup'),
    path('staff/trip/<int:trip_id>/complete/', views.complete_trip, name='complete_trip'),
    path('staff/trip/<int:trip_id>/summary/', views.trip_summary, name='trip_summary'),

    # School Admin
    path('manage/', views.manage_buses, name='manage_buses'),
    path('manage/add/', views.add_bus, name='add_bus'),
    path('manage/edit/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('students/', views.manage_students, name='manage_students'),
    path('students/add/', views.add_student, name='add_student'),
    path('trips/', views.trip_history, name='trip_history'),
]
