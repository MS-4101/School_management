from django.db import models
from django.conf import settings
from django.utils import timezone


class Lab(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EquipmentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Equipment Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class EquipmentSubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Equipment Sub-Categories'
        ordering = ['category', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('decommissioned', 'Decommissioned'),
    ]
    name = models.CharField(max_length=200)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='equipment')
    category = models.ForeignKey(EquipmentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    sub_category = models.ForeignKey(EquipmentSubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    inventory_item = models.ForeignKey(
        'inventory.Commodity', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lab_equipment', help_text='Linked inventory commodity'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.lab.name})"

    @property
    def total_units(self):
        return self.units.count()

    @property
    def available_quantity(self):
        return self.units.filter(status='available').count()


class LabUnit(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('decommissioned', 'Decommissioned'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='units')
    po_item = models.ForeignKey(
        'inventory.PurchaseOrderItem', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lab_units'
    )
    internal_uid = models.CharField(max_length=100, unique=True, verbose_name='Internal UID')
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition_status = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    last_calibrated = models.DateField(null=True, blank=True)
    added_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lab Unit'
        ordering = ['internal_uid']

    def __str__(self):
        return f"{self.equipment.name} ({self.internal_uid})"


class LabBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bookings')
    lab_unit = models.ForeignKey(LabUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_bookings')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_bookings'
    )
    purpose = models.TextField()
    quantity_booked = models.PositiveIntegerField(default=1)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.equipment.name} - {self.user} ({self.status})"


class DamageLog(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('repairing', 'Repairing'),
        ('written_off', 'Written Off'),
    ]
    lab_unit = models.ForeignKey(LabUnit, on_delete=models.CASCADE, related_name='damage_logs')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='reported_lab_damages'
    )
    damage_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')

    class Meta:
        ordering = ['-damage_date']

    def __str__(self):
        return f"Damage: {self.lab_unit.internal_uid} ({self.status})"
