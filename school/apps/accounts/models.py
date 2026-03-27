from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class Permission(models.Model):
    """Dynamic permissions that can be assigned to roles."""
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """Dynamic roles with assignable permissions."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Unified user model combining Library RBAC and Bus Tracker roles.
    Supports dynamic RBAC via M2M roles *and* shortcut role field.
    """
    ROLE_SCHOOL = 'school'
    ROLE_BUS_STAFF = 'bus_staff'
    ROLE_PARENT = 'parent'
    ROLE_LIBRARIAN = 'librarian'
    ROLE_LAB_ADMIN = 'lab_admin'

    ROLE_CHOICES = [
        (ROLE_SCHOOL, 'School Admin'),
        (ROLE_BUS_STAFF, 'Bus Staff'),
        (ROLE_PARENT, 'Parent/Guardian'),
        (ROLE_LIBRARIAN, 'Librarian'),
        (ROLE_LAB_ADMIN, 'Lab Admin'),
    ]

    # ── Library fields ────────────────────────────────────────
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    roles = models.ManyToManyField(Role, blank=True, related_name='users')
    department = models.CharField(max_length=150, blank=True)
    student_id = models.CharField(max_length=50, blank=True, verbose_name='Student / Employee ID')

    # ── Bus Tracker fields ────────────────────────────────────
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, default='')
    whatsapp_number = models.CharField(
        max_length=15, blank=True, null=True,
        help_text="With country code e.g. +919876543210"
    )

    # ── Timestamps ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    # ── Dynamic RBAC methods (from library) ───────────────────
    def has_role(self, role_name):
        return self.roles.filter(name__iexact=role_name).exists()

    def has_perm_code(self, codename):
        return self.roles.filter(permissions__codename=codename).exists()

    def has_section_access(self, section_codename, required_level='view'):
        """
        Check if user has a specific access level for a section codename.
        Levels: 'none' < 'view' < 'full'
        """
        if self.is_superuser:
            return True
            
        from .models import SectionPermission
        # Get all relevant permissions for this user's roles
        # Note: we use iexact for codename and filter by access_level
        levels = ['none', 'view', 'full']
        req_idx = levels.index(required_level)
        
        # Any role that gives the required level (or higher) grants access
        # We'll check if any role gives 'full' (idx 2) or 'view' (idx 1) if req is 'view'
        eligible_levels = levels[req_idx:]
        
        # 1. Check direct access or child-of-parent access
        # First, try to find the section to see its parent
        from .models import Section
        section = Section.objects.filter(codename__iexact=section_codename).first()
        
        query = models.Q(section__codename__iexact=section_codename)
        if section and section.parent:
            # If it's a child, also check if user has access to the parent
            query |= models.Q(section=section.parent)
            
        return SectionPermission.objects.filter(
            models.Q(role__users=self) &
            query &
            models.Q(access_level__in=eligible_levels)
        ).exists()

    def get_all_permissions_list(self):
        return Permission.objects.filter(roles__users=self).distinct()

    # ── Shortcut properties (from bus tracker) ────────────────
    @property
    def is_school_admin(self):
        return self.role == self.ROLE_SCHOOL or self.has_role('School Admin')

    @property
    def is_bus_staff(self):
        return self.role == self.ROLE_BUS_STAFF or self.has_role('Bus Staff')

    @property
    def is_parent(self):
        return self.role == self.ROLE_PARENT or self.has_role('Parent')

    @property
    def is_librarian(self):
        return self.role == self.ROLE_LIBRARIAN or self.has_role('Librarian')

    @property
    def is_lab_admin(self):
        return self.role == self.ROLE_LAB_ADMIN or self.has_role('Lab Admin')



class Section(models.Model):
    """Represents a navigable module section or subsection in the platform."""
    ACCESS_NONE = 'none'
    ACCESS_VIEW = 'view'
    ACCESS_FULL = 'full'

    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=60, default='fa-circle')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='subsections'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def is_parent_section(self):
        return self.parent is None


class SectionPermission(models.Model):
    """Defines what access level a Role has for a specific Section."""
    ACCESS_CHOICES = [
        ('none', _('No Access')),
        ('view', _('View Only')),
        ('full', _('Full Access')),
    ]

    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name='section_permissions'
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='role_permissions'
    )
    access_level = models.CharField(
        max_length=10, choices=ACCESS_CHOICES, default='none'
    )

    class Meta:
        unique_together = ('role', 'section')
        ordering = ['role', 'section__order']

    def __str__(self):
        return f"{self.role.name} → {self.section.name}: {self.access_level}"


class School(models.Model):
    """School entity — acts as tenant for bus tracker resources."""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    admin_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='school')
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    school_start_time = models.TimeField(default='08:00')
    school_end_time = models.TimeField(default='14:00')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ParentProfile(models.Model):
    """Parent profile linked to a school (for bus tracker)."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='parents')
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)
    receive_whatsapp = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Parent"
