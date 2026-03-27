import logging
from django.conf import settings
from .models import NotificationLog

logger = logging.getLogger(__name__)


def send_whatsapp_message(to_number, message, notification_log=None):
    """Send a WhatsApp message via Twilio."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        whatsapp_to = f"whatsapp:{to_number}" if not to_number.startswith('whatsapp:') else to_number
        msg = client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=whatsapp_to
        )
        if notification_log:
            notification_log.status = 'sent'
            notification_log.twilio_sid = msg.sid
            notification_log.save()
        return True
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        if notification_log:
            notification_log.status = 'failed'
            notification_log.save()
        return False


def notify_bus_departed(trip):
    """Notify all parents when bus departs."""
    from apps.buses.models import Student
    students = Student.objects.filter(bus=trip.bus, is_active=True)
    for student in students:
        if student.parent_whatsapp:
            message = (
                f"🚌 *Bus Departed*\n\n"
                f"Bus *{trip.bus.bus_name}* ({trip.bus.bus_number}) has departed.\n"
                f"Trip: {trip.get_trip_type_display()}\n"
                f"Student: {student.name} ({student.class_name})\n"
                f"Date: {trip.date.strftime('%d %b %Y')}\n\n"
                f"_You will be notified when your child boards._"
            )
            log = NotificationLog.objects.create(
                notification_type='bus_departed',
                recipient_phone=student.parent_whatsapp,
                recipient_name=student.parent_name or student.name,
                message=message,
                trip=trip,
                student=student,
            )
            send_whatsapp_message(student.parent_whatsapp, message, log)


def notify_student_picked(pickup):
    """Notify parent when student is picked up."""
    student = pickup.student
    if student.parent_whatsapp:
        message = (
            f"✅ *Student Picked Up*\n\n"
            f"*{student.name}* ({student.class_name}) has been picked up.\n"
            f"Bus: {pickup.trip.bus.bus_name}\n"
            f"Time: {pickup.picked_at.strftime('%I:%M %p') if pickup.picked_at else 'N/A'}\n\n"
            f"_Your child is safely on the bus._"
        )
        log = NotificationLog.objects.create(
            notification_type='student_picked',
            recipient_phone=student.parent_whatsapp,
            recipient_name=student.parent_name or student.name,
            message=message,
            trip=pickup.trip,
            student=student,
            pickup=pickup,
        )
        send_whatsapp_message(student.parent_whatsapp, message, log)


def notify_student_dropped(pickup):
    """Notify parent when student is dropped off."""
    student = pickup.student
    if student.parent_whatsapp:
        message = (
            f"🏠 *Student Dropped Off*\n\n"
            f"*{student.name}* ({student.class_name}) has been dropped off.\n"
            f"Bus: {pickup.trip.bus.bus_name}\n"
            f"Time: {pickup.dropped_at.strftime('%I:%M %p') if pickup.dropped_at else 'N/A'}\n\n"
            f"_Your child has reached safely._"
        )
        log = NotificationLog.objects.create(
            notification_type='student_dropped',
            recipient_phone=student.parent_whatsapp,
            recipient_name=student.parent_name or student.name,
            message=message,
            trip=pickup.trip,
            student=student,
            pickup=pickup,
        )
        send_whatsapp_message(student.parent_whatsapp, message, log)


def notify_trip_completed(trip):
    """Notify school admin when trip is completed."""
    school = trip.bus.school
    admin_user = school.admin_user
    if admin_user.whatsapp_number:
        total = trip.pickups.count()
        picked = trip.pickups.filter(status='picked').count()
        dropped = trip.pickups.filter(status='dropped').count()
        absent = trip.pickups.filter(status='absent').count()
        message = (
            f"📊 *Trip Completed*\n\n"
            f"Bus: *{trip.bus.bus_name}* ({trip.bus.bus_number})\n"
            f"Trip: {trip.get_trip_type_display()}\n"
            f"Date: {trip.date.strftime('%d %b %Y')}\n\n"
            f"Students: {total}\n"
            f"✅ Picked: {picked}\n"
            f"🏠 Dropped: {dropped}\n"
            f"❌ Absent: {absent}\n\n"
            f"_Trip completed at {trip.completed_at.strftime('%I:%M %p') if trip.completed_at else 'N/A'}_"
        )
        log = NotificationLog.objects.create(
            notification_type='trip_completed',
            recipient_phone=admin_user.whatsapp_number,
            recipient_name=admin_user.get_full_name(),
            message=message,
            trip=trip,
        )
        send_whatsapp_message(admin_user.whatsapp_number, message, log)
