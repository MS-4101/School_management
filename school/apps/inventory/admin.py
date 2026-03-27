from django.contrib import admin
from .models import Category, Commodity, StockTransaction, Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('item_category', 'item_name', 'quantity', 'unit_price', 'tax_percentage', 'linked_book', 'linked_equipment')


@admin.register(Category)
class InvCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_stock', 'unit', 'low_stock_threshold')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('commodity', 'transaction_type', 'quantity', 'user', 'timestamp')
    list_filter = ('transaction_type', 'timestamp', 'commodity')
    search_fields = ('commodity__name', 'notes')
    readonly_fields = ('timestamp',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor_code', 'contact_person', 'email', 'phone', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'vendor_code', 'contact_person', 'email')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'status', 'order_date', 'grand_total', 'created_by')
    list_filter = ('status', 'order_date', 'supplier')
    search_fields = ('po_number', 'supplier__name', 'notes')
    readonly_fields = ('po_number', 'grand_total', 'created_at', 'updated_at')
    inlines = [PurchaseOrderItemInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_order', 'item_category', 'item_name', 'quantity', 'received_qty')
    list_filter = ('item_category', 'purchase_order__status')
    search_fields = ('item_name', 'purchase_order__po_number')
