from django.db import models
from apps.buses.models import BusTrip, Student, StudentPickup


class NotificationLog(models.Model):
    NOTIFICATION_TYPES = [
        ('bus_departed', 'Bus Departed'),
        ('student_picked', 'Student Picked'),
        ('student_dropped', 'Student Dropped'),
        ('trip_completed', 'Trip Completed'),
        ('general', 'General'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    recipient_phone = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    twilio_sid = models.CharField(max_length=100, blank=True, null=True)
    trip = models.ForeignKey(BusTrip, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    pickup = models.ForeignKey(StudentPickup, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} → {self.recipient_name} ({self.status})"
