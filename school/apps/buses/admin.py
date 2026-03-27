from django.contrib import admin
from .models import Bus, BusStaff, Route, RouteStop, Student, BusTrip, StudentPickup


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_name', 'bus_number', 'school', 'status', 'capacity')
    list_filter = ('status', 'school')
    search_fields = ('bus_name', 'bus_number')


@admin.register(BusStaff)
class BusStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'bus', 'role', 'is_active')
    list_filter = ('role', 'is_active')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'bus', 'is_active')


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'order', 'landmark')
    list_filter = ('route',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_name', 'school', 'bus', 'parent_name', 'is_active')
    list_filter = ('school', 'bus', 'is_active')
    search_fields = ('name', 'parent_name', 'parent_phone')


@admin.register(BusTrip)
class BusTripAdmin(admin.ModelAdmin):
    list_display = ('bus', 'trip_type', 'date', 'status', 'total_students', 'students_picked')
    list_filter = ('status', 'trip_type', 'date')


@admin.register(StudentPickup)
class StudentPickupAdmin(admin.ModelAdmin):
    list_display = ('student', 'trip', 'status', 'pickup_time', 'drop_time')
    list_filter = ('status',)
