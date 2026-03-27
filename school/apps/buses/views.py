from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from functools import wraps
from .models import Bus, BusStaff, Student, BusTrip, StudentPickup, Route, RouteStop
from apps.accounts.models import School
from apps.accounts.decorators import section_required


def bus_login_required(view_func):
    """Decorator: only allow bus-session login."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('bus_login'):
            messages.error(request, 'Please login as bus staff first.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ─── Staff Dashboard ─────────────────────────────────────────

@bus_login_required
def staff_dashboard(request):
    bus_id = request.session.get('bus_id')
    bus = get_object_or_404(Bus, id=bus_id)
    today = timezone.now().date()
    # Categorize trips for today
    morning_trip = BusTrip.objects.filter(bus=bus, date=today, trip_type='morning').first()
    afternoon_trip = BusTrip.objects.filter(bus=bus, date=today, trip_type='afternoon').first()
    
    context = {
        'bus': bus,
        'morning_trip': morning_trip,
        'afternoon_trip': afternoon_trip,
        'today': today,
        'total_students': Student.objects.filter(bus=bus, is_active=True).count()
    }
    return render(request, 'buses/staff_dashboard.html', context)


@bus_login_required
def start_trip(request):
    if request.method == 'POST':
        bus_id = request.session.get('bus_id')
        bus = get_object_or_404(Bus, id=bus_id)
        trip_type = request.POST.get('trip_type', 'morning')
        today = timezone.now().date()

        existing = BusTrip.objects.filter(bus=bus, date=today, trip_type=trip_type).first()
        if existing:
            messages.warning(request, f'{existing.get_trip_type_display()} trip already exists for today.')
            return redirect('buses:trip_detail', trip_id=existing.id)

        students = Student.objects.filter(bus=bus, is_active=True)
        trip = BusTrip.objects.create(
            bus=bus, trip_type=trip_type, date=today,
            started_at=timezone.now(), total_students=students.count()
        )
        for student in students:
            StudentPickup.objects.create(trip=trip, student=student)

        try:
            from apps.notifications.services import notify_bus_departed
            notify_bus_departed(trip)
        except Exception:
            pass

        messages.success(request, f'{trip.get_trip_type_display()} trip started!')
        return redirect('buses:trip_detail', trip_id=trip.id)
    return redirect('buses:staff_dashboard')


@bus_login_required
def trip_detail(request, trip_id):
    trip = get_object_or_404(BusTrip, id=trip_id)
    
    # Sync students if trip is active
    if trip.status == 'active':
        assigned_students = Student.objects.filter(bus=trip.bus, is_active=True)
        existing_pickup_student_ids = trip.pickups.values_list('student_id', flat=True)
        
        new_pickups = []
        for student in assigned_students:
            if student.id not in existing_pickup_student_ids:
                new_pickups.append(StudentPickup(trip=trip, student=student))
        
        if new_pickups:
            StudentPickup.objects.bulk_create(new_pickups)
            trip.total_students = trip.pickups.count()
            trip.save()

    pickups = trip.pickups.select_related('student', 'student__route_stop').all()
    
    # Prepare pickups with display data
    for p in pickups:
        if p.student.route_stop:
            p.location_display = p.student.route_stop.name
        else:
            p.location_display = p.student.address
    
    # Pre-calculate data for template to avoid complex logic
    total_count = pickups.count()
    picked_count = pickups.filter(status='picked').count()
    dropped_count = pickups.filter(status='dropped').count()
    absent_count = pickups.filter(status='absent').count()
    pending_count = pickups.filter(status='pending').count()
    
    progress_percent = 0
    if total_count > 0:
        progress_percent = int((picked_count + dropped_count) / total_count * 100)

    context = {
        'trip': trip, 
        'pickups': pickups,
        'bus': trip.bus,
        'total_count': total_count,
        'picked_count': picked_count,
        'dropped_count': dropped_count,
        'absent_count': absent_count,
        'pending_count': pending_count,
        'progress_percent': progress_percent,
    }
    return render(request, 'buses/trip_detail.html', context)


from django.http import JsonResponse

@bus_login_required
def mark_pickup(request, pickup_id):
    if request.method == 'POST':
        pickup = get_object_or_404(StudentPickup, id=pickup_id)
        action = request.POST.get('action') # 'picked', 'dropped', 'absent'
        location = request.POST.get('location', '')

        if action == 'picked':
            pickup.status = 'picked'
            pickup.pickup_time = timezone.now()
            pickup.pickup_location = location
            pickup.save()
            try:
                from apps.notifications.services import notify_student_picked
                notify_student_picked(pickup)
            except Exception: pass
            
        elif action == 'dropped':
            pickup.status = 'dropped'
            pickup.drop_time = timezone.now()
            pickup.drop_location = location
            pickup.save()
            try:
                from apps.notifications.services import notify_student_dropped
                notify_student_dropped(pickup)
            except Exception: pass
            
        elif action == 'absent':
            pickup.status = 'absent'
            pickup.save()

        # Update trip stats
        trip = pickup.trip
        trip.students_picked = trip.pickups.filter(status='picked').count()
        trip.students_dropped = trip.pickups.filter(status='dropped').count()
        trip.students_absent = trip.pickups.filter(status='absent').count()
        trip.save()

        return JsonResponse({
            'success': True,
            'status': pickup.status,
            'message': f'{pickup.student.name} marked as {pickup.get_status_display()}.'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@bus_login_required
def complete_trip(request, trip_id):
    if request.method == 'POST':
        trip = get_object_or_404(BusTrip, id=trip_id)
        trip.status = 'completed'
        trip.completed_at = timezone.now()
        trip.save()
        try:
            from apps.notifications.services import notify_trip_completed
            notify_trip_completed(trip)
        except Exception:
            pass
        messages.success(request, 'Trip completed successfully!')
        return redirect('buses:trip_summary', trip_id=trip.id)
    return redirect('buses:staff_dashboard')


@bus_login_required
def trip_summary(request, trip_id):
    trip = get_object_or_404(BusTrip, id=trip_id)
    pickups = trip.pickups.select_related('student').all()
    
    context = {
        'trip': trip,
        'bus': trip.bus,
        'picked_list': pickups.filter(status='picked'),
        'dropped_list': pickups.filter(status='dropped'),
        'absent_list': pickups.filter(status='absent'),
        'pending_list': pickups.filter(status='pending'),
    }
    return render(request, 'buses/trip_summary.html', context)


# ─── School Admin: Bus Management ────────────────────────────

@login_required
@section_required('bus', 'view')
def manage_buses(request):
    school = request.school
    if not school:
        messages.error(request, 'No school associated.')
        return redirect('dashboard:home')
    buses = Bus.objects.filter(school=school)
    return render(request, 'buses/manage_buses.html', {'buses': buses})


@login_required
@section_required('bus', 'full')
def add_bus(request):
    school = request.school
    if not school:
        messages.error(request, 'No school associated.')
        return redirect('dashboard:home')
    if request.method == 'POST':
        bus = Bus(
            school=school,
            bus_name=request.POST.get('bus_name', ''),
            bus_number=request.POST.get('bus_number', ''),
            capacity=int(request.POST.get('capacity', 40)),
            login_id=request.POST.get('login_id', ''),
            login_password=make_password(request.POST.get('login_password', '')),
        )
        bus.save()

        # Add staff
        for i in range(1, 3):
            staff_name = request.POST.get(f'staff_name_{i}')
            if staff_name:
                BusStaff.objects.create(
                    bus=bus,
                    name=staff_name,
                    phone=request.POST.get(f'staff_phone_{i}', ''),
                    role=request.POST.get(f'staff_role_{i}', 'driver')
                )

        messages.success(request, f'Bus {bus.bus_name} added successfully.')
        return redirect('buses:manage_buses')
    return render(request, 'buses/add_bus.html')


@login_required
@section_required('bus', 'full')
def edit_bus(request, bus_id):
    school = request.school
    bus = get_object_or_404(Bus, id=bus_id, school=school)

    if request.method == 'POST':
        bus.bus_name = request.POST.get('bus_name', bus.bus_name)
        bus.bus_number = request.POST.get('bus_number', bus.bus_number)
        bus.capacity = int(request.POST.get('capacity', bus.capacity))
        bus.status = request.POST.get('status', bus.status)
        bus.login_id = request.POST.get('login_id', bus.login_id)

        new_password = request.POST.get('login_password')
        if new_password:
            bus.login_password = make_password(new_password)

        bus.save()

        # Update staff - simple approach: delete existing and recreate
        # (This is easier than matching IDs from a form that doesn't provide them)
        bus.staff.all().delete()
        for i in range(1, 3):
            staff_name = request.POST.get(f'staff_name_{i}')
            if staff_name:
                BusStaff.objects.create(
                    bus=bus,
                    name=staff_name,
                    phone=request.POST.get(f'staff_phone_{i}', ''),
                    role=request.POST.get(f'staff_role_{i}', 'driver')
                )

        messages.success(request, f'Bus {bus.bus_name} updated successfully.')
        return redirect('buses:manage_buses')

    # Prefill staff data for the template
    staff_list = list(bus.staff.all())
    context = {
        'bus': bus,
        'staff_1': staff_list[0] if len(staff_list) > 0 else None,
        'staff_2': staff_list[1] if len(staff_list) > 1 else None,
    }
    return render(request, 'buses/edit_bus.html', context)


@login_required
@section_required('bus.students', 'view')
def manage_students(request):
    school = request.school
    if not school:
        messages.error(request, 'No school associated.')
        return redirect('dashboard:home')
    students = Student.objects.filter(school=school).select_related('bus')
    return render(request, 'buses/manage_students.html', {'students': students})


@login_required
@section_required('bus.students', 'full')
def add_student(request):
    school = request.school
    if not school:
        messages.error(request, 'No school associated.')
        return redirect('dashboard:home')
    buses = Bus.objects.filter(school=school, status='active')
    if request.method == 'POST':
        # Mapping template fields to model fields
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip()

        student = Student(
            school=school,
            name=full_name,
            class_name=request.POST.get('class_name', ''),
            section=request.POST.get('section', ''),
            roll_number=request.POST.get('student_id', ''),
            parent_name=request.POST.get('parent_name', ''),
            parent_phone=request.POST.get('parent_phone', ''),
            parent_whatsapp=request.POST.get('parent_whatsapp', ''),
            address=request.POST.get('address', '') or request.POST.get('pickup_location', ''),
        )
        bus_id = request.POST.get('bus_id')
        if bus_id:
            student.bus = get_object_or_404(Bus, id=bus_id, school=school)
        student.save()
        messages.success(request, f'Student {student.name} added.')
        return redirect('buses:manage_students')
    return render(request, 'buses/add_student.html', {'buses': buses})


@login_required
@section_required('bus', 'view')
def trip_history(request):
    school = request.school
    trips = BusTrip.objects.filter(bus__school=school).select_related('bus').order_by('-date')[:50]
    return render(request, 'buses/trip_history.html', {'trips': trips})
