import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.hashers import check_password
from .models import CustomUser, Role, Permission, Section, SectionPermission, School
from .forms import (
    LoginForm, RegisterForm, UserEditForm, ProfileForm,
    RoleForm, PermissionForm, UserCreateForm, SchoolCreateForm
)
from .decorators import role_required


# ─── Authentication ──────────────────────────────────────────

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Unified single-form login — auto-detects role from credentials."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    if request.session.get('bus_login'):
        return redirect('buses:staff_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 1. Try Bus Staff (session-based, no Django user)
        try:
            from apps.buses.models import Bus
            bus = Bus.objects.get(login_id=username, school__is_active=True)
            if check_password(password, bus.login_password):
                request.session['bus_id'] = bus.id
                request.session['bus_login'] = True
                request.session['bus_name'] = bus.bus_name
                request.session['bus_number'] = bus.bus_number
                request.session['school_name'] = bus.school.name
                messages.success(request, f'Welcome! {bus.bus_name} logged in successfully.')
                return redirect('buses:staff_dashboard')
        except Exception:
            pass

        # 2. Try Django user
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid credentials. Please check your username and password.')

    return render(request, 'accounts/login.html')


def redirect_by_role(user):
    """Route user to appropriate dashboard based on role."""
    if user.is_superuser or user.has_role('Admin'):
        return redirect('dashboard:home')
    if user.is_school_admin:
        return redirect('dashboard:school_dashboard')
    if user.is_parent:
        return redirect('dashboard:parent_dashboard')
    return redirect('dashboard:home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            default_role = Role.objects.filter(name__iexact='member').first()
            if default_role:
                user.roles.add(default_role)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    if 'bus_login' in request.session:
        request.session.flush()
    else:
        logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def bus_logout_view(request):
    request.session.flush()
    messages.success(request, 'Bus session ended successfully.')
    return redirect('accounts:login')


# ─── Profile ─────────────────────────────────────────────────

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# ─── User Management ─────────────────────────────────────────

@login_required
@role_required('Admin')
def user_list(request):
    users = CustomUser.objects.all()
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            models.Q(username__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    return render(request, 'accounts/user_list.html', {'users': users, 'search': search})


@login_required
@role_required('Admin')
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user}" updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'accounts/user_edit.html', {'form': form, 'edit_user': user})


@login_required
@role_required('Admin')
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'edit_user': user})


# ─── Role Management ─────────────────────────────────────────

@login_required
@role_required('Admin')
def role_list(request):
    roles = Role.objects.prefetch_related('permissions').all()
    return render(request, 'accounts/role_list.html', {'roles': roles})


@login_required
@role_required('Admin')
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully.')
            return redirect('accounts:role_list')
    else:
        form = RoleForm()
    return render(request, 'accounts/role_form.html', {'form': form, 'title': 'Create Role'})


@login_required
@role_required('Admin')
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f'Role "{role.name}" updated successfully.')
            return redirect('accounts:role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'accounts/role_form.html', {'form': form, 'title': f'Edit Role: {role.name}'})


@login_required
@role_required('Admin')
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Role deleted successfully.')
        return redirect('accounts:role_list')
    return render(request, 'accounts/role_confirm_delete.html', {'role': role})


# ─── Permission Management ───────────────────────────────────

@login_required
@role_required('Admin')
def permission_list(request):
    permissions = Permission.objects.all()
    return render(request, 'accounts/permission_list.html', {'permissions': permissions})


@login_required
@role_required('Admin')
def permission_create(request):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Permission created successfully.')
            return redirect('accounts:permission_list')
    else:
        form = PermissionForm()
    return render(request, 'accounts/permission_form.html', {'form': form, 'title': 'Create Permission'})


@login_required
@role_required('Admin')
def permission_delete(request, pk):
    perm = get_object_or_404(Permission, pk=pk)
    if request.method == 'POST':
        perm.delete()
        messages.success(request, 'Permission deleted.')
        return redirect('accounts:permission_list')
    return render(request, 'accounts/permission_confirm_delete.html', {'permission': perm})


# ─── Access Control Hub ──────────────────────────────────────

@login_required
@role_required('Admin')
def access_control(request):
    """
    Unified Access Control panel with 3 tabs:
      - user_creation : create users + assign role
      - role_permission: matrix of sections x access_level per role
      - school_creation: create school tenants
    """
    active_tab = request.GET.get('tab', 'user_creation')

    # Forms
    user_form = UserCreateForm()
    school_form = SchoolCreateForm()

    # Data for role permission tab
    roles = Role.objects.all()
    parent_sections = Section.objects.filter(parent__isnull=True).prefetch_related('subsections')
    selected_role_id = request.GET.get('role_id')
    selected_role = None
    permission_map = {}  # {section_id: access_level}

    if selected_role_id:
        try:
            # Use filter instead of get to avoid DoesNotExist, but cast to int to prevent ValueError
            selected_role = Role.objects.filter(pk=int(selected_role_id)).first()
        except (ValueError, TypeError):
            selected_role = None
        if selected_role:
            sp_qs = SectionPermission.objects.filter(role=selected_role)
            permission_map = {sp.section_id: sp.access_level for sp in sp_qs}

    schools = School.objects.all().order_by('name')

    context = {
        'active_tab': active_tab,
        'user_form': user_form,
        'school_form': school_form,
        'roles': roles,
        'parent_sections': parent_sections,
        'selected_role': selected_role,
        'permission_map': permission_map,
        'schools': schools,
    }
    return render(request, 'dashboard/access_control.html', context)


@login_required
@role_required('Admin')
def create_user(request):
    """POST handler: create new user with role."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{form.cleaned_data["username"]}" created successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect(f"{request.META.get('HTTP_REFERER', '/access-control/')}?tab=user_creation")


@login_required
@role_required('Admin')
def create_school(request):
    """POST handler: create new school/tenant."""
    if request.method == 'POST':
        form = SchoolCreateForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save()
            messages.success(request, f'School "{school.name}" created successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect(f"{request.META.get('HTTP_REFERER', '/access-control/')}?tab=school_creation")


@login_required
@role_required('Admin')
@require_POST
def save_role_permissions(request):
    """AJAX POST: save section permission matrix for a role."""
    try:
        data = json.loads(request.body)
        role_id = data.get('role_id')
        permissions = data.get('permissions', {})  # {section_id: access_level}

        role = get_object_or_404(Role, pk=role_id)

        for section_id_str, access_level in permissions.items():
            section = Section.objects.filter(pk=int(section_id_str)).first()
            if section and access_level in ('none', 'view', 'full'):
                SectionPermission.objects.update_or_create(
                    role=role, section=section,
                    defaults={'access_level': access_level}
                )

        return JsonResponse({'status': 'ok', 'message': f'Permissions saved for role "{role.name}".'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@role_required('Admin')
@require_POST
def create_role_with_permissions(request):
    """AJAX POST: Create a new role and save its section permissions."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        permissions = data.get('permissions', {})  # {section_id: access_level}

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Role name is required.'}, status=400)

        # Create the role
        role, created = Role.objects.get_or_create(name=name, defaults={'description': description})
        if not created:
            return JsonResponse({'status': 'error', 'message': f'Role "{name}" already exists.'}, status=400)

        # Save section permissions
        for section_id_str, access_level in permissions.items():
            section = Section.objects.filter(pk=int(section_id_str)).first()
            if section and access_level in ('none', 'view', 'full'):
                SectionPermission.objects.create(
                    role=role, section=section, access_level=access_level
                )

        return JsonResponse({'status': 'ok', 'message': f'Role "{role.name}" created with permissions.', 'role_id': role.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
