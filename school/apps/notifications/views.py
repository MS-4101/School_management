from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import NotificationLog


@login_required
def notification_logs(request):
    school = request.school
    if school:
        logs = NotificationLog.objects.filter(
            trip__bus__school=school
        ).select_related('trip', 'student', 'pickup').order_by('-created_at')[:100]
    else:
        logs = NotificationLog.objects.all().order_by('-created_at')[:100]
    return render(request, 'notifications/logs.html', {'logs': logs})
