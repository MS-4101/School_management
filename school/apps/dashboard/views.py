from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def landing_page(request):
    """Common landing page for the unified school platform."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.session.get('bus_login'):
        return redirect('buses:staff_dashboard')
    return render(request, 'landing/index.html')


@login_required
def home(request):
    """Unified admin/librarian/lab-admin dashboard with all module stats."""
    context = {}

    # Library stats
    try:
        from apps.library_mgmt.models import Book, BookIssue, BookCopy
        context['total_books'] = Book.objects.count()
        context['books_issued'] = BookIssue.objects.filter(status='issued').count()
        context['books_overdue'] = BookIssue.objects.filter(status='overdue').count()
        context['total_book_copies'] = BookCopy.objects.count()
    except Exception:
        context['total_books'] = 0

    # Lab stats
    try:
        from apps.lab_mgmt.models import Lab, Equipment, LabBooking
        context['total_labs'] = Lab.objects.filter(is_active=True).count()
        context['total_equipment'] = Equipment.objects.count()
        context['pending_bookings'] = LabBooking.objects.filter(status='pending').count()
    except Exception:
        context['total_labs'] = 0

    # Inventory stats
    try:
        from apps.inventory.models import Commodity
        from django.db.models import F
        context['total_commodities'] = Commodity.objects.count()
        context['low_stock'] = Commodity.objects.filter(current_stock__lte=F('low_stock_threshold')).count()
    except Exception:
        context['total_commodities'] = 0

    # User stats
    try:
        from apps.accounts.models import CustomUser
        context['total_users'] = CustomUser.objects.count()
    except Exception:
        context['total_users'] = 0

    # Bus stats (if school admin)
    if request.user.is_school_admin or request.user.is_superuser:
        try:
            from apps.buses.models import Bus, Student, BusTrip
            school = request.school
            if school:
                context['total_buses'] = Bus.objects.filter(school=school).count()
                context['total_students_bus'] = Student.objects.filter(school=school, is_active=True).count()
                today = timezone.now().date()
                context['trips_today'] = BusTrip.objects.filter(bus__school=school, date=today).count()
        except Exception:
            pass

    return render(request, 'dashboard/home.html', context)


@login_required
def school_dashboard(request):
    """School admin dashboard (bus tracker focus)."""
    school = request.school
    context = {'school': school}
    if school:
        try:
            from apps.buses.models import Bus, Student, BusTrip
            from apps.notifications.models import NotificationLog
            today = timezone.now().date()
            buses = Bus.objects.filter(school=school)
            context['total_buses'] = buses.count()
            context['active_buses'] = buses.filter(status='active').count()
            context['total_students'] = Student.objects.filter(school=school, is_active=True).count()
            context['trips_today'] = BusTrip.objects.filter(bus__school=school, date=today).count()
            context['active_trips'] = BusTrip.objects.filter(
                bus__school=school, date=today, status='active'
            ).select_related('bus')
            context['recent_notifications'] = NotificationLog.objects.filter(
                trip__bus__school=school
            ).order_by('-created_at')[:10]
        except Exception:
            pass
    return render(request, 'dashboard/school_dashboard.html', context)


@login_required
def parent_dashboard(request):
    """Parent dashboard — children status and notifications."""
    context = {}
    try:
        from apps.buses.models import Student, StudentPickup
        from apps.notifications.models import NotificationLog
        parent_profile = getattr(request.user, 'parent_profile', None)
        if parent_profile:
            children = Student.objects.filter(parent_profile=parent_profile, is_active=True)
            context['children'] = children
            today = timezone.now().date()
            for child in children:
                latest_pickup = StudentPickup.objects.filter(
                    student=child, trip__date=today
                ).select_related('trip').order_by('-trip__started_at').first()
                child.today_status = latest_pickup
            context['recent_notifications'] = NotificationLog.objects.filter(
                student__parent_profile=parent_profile
            ).order_by('-created_at')[:10]
    except Exception:
        pass
    return render(request, 'dashboard/parent_dashboard.html', context)
