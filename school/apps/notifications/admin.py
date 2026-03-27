from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'recipient_name', 'recipient_phone', 'status', 'created_at')
    list_filter = ('notification_type', 'status')
    search_fields = ('recipient_name', 'recipient_phone', 'message')
    readonly_fields = ('twilio_sid', 'created_at')
