from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Lab, Equipment, EquipmentCategory, EquipmentSubCategory, LabBooking, LabUnit
from .forms import LabForm, EquipmentForm, EquipmentCategoryForm, EquipmentSubCategoryForm, LabBookingForm
from apps.accounts.decorators import section_required


# ─── Labs ────────────────────────────────────────────────────

@login_required
@section_required('lab', 'view')
def lab_list(request):
    labs = Lab.objects.prefetch_related('equipment').all()
    return render(request, 'lab_mgmt/lab_list.html', {'labs': labs})


@login_required
@section_required('lab.labs', 'full')
def lab_create(request):
    if request.method == 'POST':
        form = LabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab created successfully.')
            return redirect('lab:lab_list')
    else:
        form = LabForm()
    return render(request, 'lab_mgmt/lab_form.html', {'form': form, 'title': 'Add Lab'})


@login_required
@section_required('lab.labs', 'full')
def lab_edit(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab updated.')
            return redirect('lab:lab_list')
    else:
        form = LabForm(instance=lab)
    return render(request, 'lab_mgmt/lab_form.html', {'form': form, 'title': f'Edit: {lab.name}'})


@login_required
@section_required('lab.labs', 'full')
def lab_delete(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST':
        lab.delete()
        messages.success(request, 'Lab deleted.')
        return redirect('lab:lab_list')
    return render(request, 'lab_mgmt/lab_confirm_delete.html', {'lab': lab})


# ─── Equipment Categories ───────────────────────────────────

@login_required
@section_required('lab', 'view')
def eq_category_list(request):
    categories = EquipmentCategory.objects.prefetch_related('subcategories').all()
    return render(request, 'lab_mgmt/eq_category_list.html', {'categories': categories})


@login_required
@section_required('lab.categories', 'full')
def eq_category_create(request):
    if request.method == 'POST':
        form = EquipmentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment Category created.')
            return redirect('lab:eq_category_list')
    else:
        form = EquipmentCategoryForm()
    return render(request, 'lab_mgmt/eq_category_form.html', {'form': form, 'title': 'Add Equipment Category'})


@login_required
@section_required('lab.categories', 'full')
def eq_category_edit(request, pk):
    category = get_object_or_404(EquipmentCategory, pk=pk)
    if request.method == 'POST':
        form = EquipmentCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment Category updated.')
            return redirect('lab:eq_category_list')
    else:
        form = EquipmentCategoryForm(instance=category)
    return render(request, 'lab_mgmt/eq_category_form.html', {'form': form, 'title': f'Edit: {category.name}'})


@login_required
@section_required('lab.categories', 'full')
def eq_category_delete(request, pk):
    category = get_object_or_404(EquipmentCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Equipment Category deleted.')
        return redirect('lab:eq_category_list')
    return render(request, 'lab_mgmt/eq_category_confirm_delete.html', {'category': category})


# ─── Equipment Sub-Categories ───────────────────────────────

@login_required
@section_required('lab', 'view')
def eq_subcategory_list(request):
    subcategories = EquipmentSubCategory.objects.select_related('category').all()
    return render(request, 'lab_mgmt/eq_subcategory_list.html', {'subcategories': subcategories})


@login_required
@section_required('lab.subcategories', 'full')
def eq_subcategory_create(request):
    if request.method == 'POST':
        form = EquipmentSubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment Sub-Category created.')
            return redirect('lab:eq_subcategory_list')
    else:
        form = EquipmentSubCategoryForm()
    return render(request, 'lab_mgmt/eq_subcategory_form.html', {'form': form, 'title': 'Add Equipment Sub-Category'})


@login_required
@section_required('lab.subcategories', 'full')
def eq_subcategory_edit(request, pk):
    subcategory = get_object_or_404(EquipmentSubCategory, pk=pk)
    if request.method == 'POST':
        form = EquipmentSubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment Sub-Category updated.')
            return redirect('lab:eq_subcategory_list')
    else:
        form = EquipmentSubCategoryForm(instance=subcategory)
    return render(request, 'lab_mgmt/eq_subcategory_form.html', {'form': form, 'title': f'Edit: {subcategory.name}'})


@login_required
@section_required('lab.subcategories', 'full')
def eq_subcategory_delete(request, pk):
    subcategory = get_object_or_404(EquipmentSubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, 'Equipment Sub-Category deleted.')
        return redirect('lab:eq_subcategory_list')
    return render(request, 'lab_mgmt/eq_subcategory_confirm_delete.html', {'subcategory': subcategory})


@login_required
def ajax_eq_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = EquipmentSubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


# ─── Equipment ───────────────────────────────────────────────

@login_required
@section_required('lab', 'view')
def equipment_list(request):
    equipment = Equipment.objects.select_related('lab', 'category', 'sub_category').all()
    search = request.GET.get('search', '')
    lab_id = request.GET.get('lab', '')
    cat_id = request.GET.get('category', '')
    if search:
        equipment = equipment.filter(name__icontains=search)
    if lab_id:
        equipment = equipment.filter(lab_id=lab_id)
    if cat_id:
        equipment = equipment.filter(category_id=cat_id)
    labs = Lab.objects.filter(is_active=True)
    categories = EquipmentCategory.objects.all()
    return render(request, 'lab_mgmt/equipment_list.html', {
        'equipment': equipment, 'labs': labs, 'categories': categories,
        'search': search, 'selected_lab': lab_id, 'selected_category': cat_id
    })


@login_required
def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    units = equipment.units.all().order_by('internal_uid')
    bookings = equipment.bookings.select_related('user').order_by('-booking_date')[:10]
    return render(request, 'lab_mgmt/equipment_detail.html', {
        'equipment': equipment, 'units': units, 'bookings': bookings
    })


@login_required
@section_required('lab.equipment', 'full')
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment added.')
            return redirect('lab:equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'lab_mgmt/equipment_form.html', {'form': form, 'title': 'Add Equipment'})


@login_required
@section_required('lab.equipment', 'full')
def equipment_edit(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=eq)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment updated.')
            return redirect('lab:equipment_list')
    else:
        form = EquipmentForm(instance=eq)
    return render(request, 'lab_mgmt/equipment_form.html', {'form': form, 'title': f'Edit: {eq.name}'})


@login_required
@section_required('lab.equipment', 'full')
def equipment_delete(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        eq.delete()
        messages.success(request, 'Equipment deleted.')
        return redirect('lab:equipment_list')
    return render(request, 'lab_mgmt/equipment_confirm_delete.html', {'equipment': eq})


# ─── Bookings ────────────────────────────────────────────────

@login_required
@section_required('lab.bookings', 'view')
def booking_list(request):
    bookings = LabBooking.objects.select_related('equipment__lab', 'user', 'approved_by').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Note: access control inheritance handles superuser/admin implicitly now via section_required
    if not request.user.has_section_access('lab.bookings', 'full'):
        bookings = bookings.filter(user=request.user)
    return render(request, 'lab_mgmt/booking_list.html', {
        'bookings': bookings, 'status_filter': status_filter
    })


@login_required
def booking_create(request):
    equipment_id = request.GET.get('equipment')
    unit_id = request.GET.get('unit')
    equipment = None
    initial_data = {}
    if equipment_id:
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        initial_data['equipment'] = equipment
    if unit_id:
        unit = get_object_or_404(LabUnit, pk=unit_id)
        initial_data['lab_unit'] = unit
        if not equipment:
            equipment = unit.equipment
            initial_data['equipment'] = equipment

    if request.method == 'POST':
        form = LabBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Booking request submitted.')
            return redirect('lab:booking_list')
    else:
        form = LabBookingForm(initial=initial_data)

    return render(request, 'lab_mgmt/booking_form.html', {
        'form': form, 'title': 'Request Equipment Booking', 'equipment': equipment
    })


@login_required
@section_required('lab.bookings', 'full')
def booking_approve(request, pk):
    booking = get_object_or_404(LabBooking, pk=pk)
    if booking.status != 'pending':
        messages.info(request, 'Booking already processed.')
        return redirect('lab:booking_list')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            if booking.equipment.available_quantity >= booking.quantity_booked:
                booking.status = 'approved'
                booking.approved_by = request.user
                if booking.lab_unit:
                    unit = booking.lab_unit
                    unit.status = 'in_use'
                    unit.save()
                else:
                    units_to_book = booking.equipment.units.filter(status='available')[:booking.quantity_booked]
                    for unit in units_to_book:
                        unit.status = 'in_use'
                        unit.save()
                        if booking.quantity_booked == 1:
                            booking.lab_unit = unit
                booking.save()
                messages.success(request, 'Booking approved.')
            else:
                messages.error(request, 'Insufficient available units.')
        elif action == 'reject':
            booking.status = 'rejected'
            booking.approved_by = request.user
            booking.notes = request.POST.get('reject_notes', '')
            booking.save()
            messages.info(request, 'Booking rejected.')
        return redirect('lab:booking_list')
    return render(request, 'lab_mgmt/booking_approve.html', {'booking': booking})


@login_required
@section_required('lab.bookings', 'full')
def booking_return(request, pk):
    booking = get_object_or_404(LabBooking, pk=pk)
    if booking.status != 'approved':
        messages.info(request, 'Booking not in approved state.')
        return redirect('lab:booking_list')
    if request.method == 'POST':
        booking.status = 'returned'
        booking.save()
        if booking.lab_unit:
            unit = booking.lab_unit
            unit.status = 'available'
            unit.save()
        messages.success(request, 'Equipment returned successfully.')
        return redirect('lab:booking_list')
    return render(request, 'lab_mgmt/booking_return.html', {'booking': booking})
