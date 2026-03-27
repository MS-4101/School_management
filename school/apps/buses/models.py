from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password
from apps.accounts.models import School, ParentProfile


class Bus(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='buses')
    bus_name = models.CharField(max_length=100)
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(default=40)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    login_id = models.CharField(max_length=100, unique=True, help_text='Bus login username')
    login_password = models.CharField(max_length=255, help_text='Hashed password')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Buses'
        ordering = ['bus_name']

    def __str__(self):
        return f"{self.bus_name} ({self.bus_number})"

    def set_password(self, raw_password):
        self.login_password = make_password(raw_password)
        self.save(update_fields=['login_password'])


class BusStaff(models.Model):
    ROLE_CHOICES = [
        ('driver', 'Driver'),
        ('attendant', 'Attendant'),
    ]
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bus_staff_roles', null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Bus Staff'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} ({self.bus})"


class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.bus})"


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} (Stop #{self.order})"


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=200)
    class_name = models.CharField(max_length=50, verbose_name='Class/Grade')
    section = models.CharField(max_length=10, blank=True)
    roll_number = models.CharField(max_length=20, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    route_stop = models.ForeignKey(RouteStop, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    parent_profile = models.ForeignKey(ParentProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='children')
    parent_name = models.CharField(max_length=200, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    parent_whatsapp = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.class_name})"


class BusTrip(models.Model):
    TRIP_TYPES = [
        ('morning', 'Morning (Home → School)'),
        ('afternoon', 'Afternoon (School → Home)'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPES)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_students = models.PositiveIntegerField(default=0)
    students_picked = models.PositiveIntegerField(default=0)
    students_dropped = models.PositiveIntegerField(default=0)
    students_absent = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-started_at']
        unique_together = ['bus', 'trip_type', 'date']

    def __str__(self):
        return f"{self.bus} - {self.get_trip_type_display()} - {self.date}"


class StudentPickup(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked', 'Picked Up'),
        ('dropped', 'Dropped Off'),
        ('absent', 'Absent'),
    ]
    trip = models.ForeignKey(BusTrip, on_delete=models.CASCADE, related_name='pickups')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='pickups')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing and Location
    pickup_time = models.DateTimeField(null=True, blank=True)
    pickup_location = models.CharField(max_length=255, blank=True)
    
    drop_time = models.DateTimeField(null=True, blank=True)
    drop_location = models.CharField(max_length=255, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['trip', 'student']

    def __str__(self):
        return f"{self.student.name} - {self.get_status_display()}"
