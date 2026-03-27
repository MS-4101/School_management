from django.contrib import admin
from .models import Lab, Equipment, EquipmentCategory, EquipmentSubCategory, LabUnit, LabBooking, DamageLog


class LabUnitInline(admin.TabularInline):
    model = LabUnit
    extra = 1
    fields = ('internal_uid', 'serial_number', 'status', 'condition_status', 'last_calibrated')


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location')


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(EquipmentSubCategory)
class EquipmentSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'lab', 'category', 'sub_category', 'status', 'quantity', 'available_quantity')
    list_filter = ('status', 'lab', 'category')
    search_fields = ('name',)
    inlines = [LabUnitInline]


@admin.register(LabUnit)
class LabUnitAdmin(admin.ModelAdmin):
    list_display = ('internal_uid', 'equipment', 'serial_number', 'status', 'condition_status', 'added_date')
    list_filter = ('status', 'condition_status', 'equipment__lab')
    search_fields = ('internal_uid', 'serial_number', 'equipment__name')


@admin.register(LabBooking)
class LabBookingAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'lab_unit', 'user', 'start_date', 'end_date', 'status', 'approved_by')
    list_filter = ('status',)


@admin.register(DamageLog)
class DamageLogAdmin(admin.ModelAdmin):
    list_display = ('lab_unit', 'reported_by', 'damage_date', 'status')
    list_filter = ('status',)
    search_fields = ('lab_unit__internal_uid', 'description')
