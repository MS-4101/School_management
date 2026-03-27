from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Commodity(models.Model):
    SOURCE_TYPES = [
        ('manual', 'Manual Entry'),
        ('library', 'Library System'),
        ('laboratory', 'Laboratory System'),
    ]
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='commodities')
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, help_text="e.g., Pieces, Liters, Packets")
    current_stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    image = models.ImageField(upload_to='inventory_items/', blank=True, null=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='manual',
                                   help_text='Where this item originates from')
    source_id = models.PositiveIntegerField(null=True, blank=True,
                                            help_text='ID of the originating Book or Equipment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Commodities'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def source_label(self):
        if self.source_type == 'library':
            return '📚 Library'
        elif self.source_type == 'laboratory':
            return '🔬 Laboratory'
        return '📋 Manual'


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('stock_in', 'Stock In (Purchase/Refill)'),
        ('issue', 'Issue (Used/Dispatched)'),
        ('return', 'Return (Back to Inventory)'),
        ('adjustment', 'Adjustment (Correction)'),
    ]
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                             related_name='inventory_transactions')
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.commodity.name} ({self.quantity})"


class Supplier(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]
    name = models.CharField(max_length=255)
    vendor_code = models.CharField(max_length=50, unique=True, help_text='Internal vendor identification code')
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True, verbose_name='GST / Tax ID')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.vendor_code})"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('partial', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    po_number = models.CharField(max_length=64, unique=True, verbose_name='PO Number',
                                 help_text='Auto-generated: PO-YYYYMMDD-XXXX')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='purchase_orders_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']

    def __str__(self):
        return f"{self.po_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self._generate_po_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_po_number():
        today = timezone.now().strftime('%Y%m%d')
        prefix = f'PO-{today}-'
        last_po = PurchaseOrder.objects.filter(po_number__startswith=prefix).order_by('-po_number').first()
        if last_po:
            last_seq = int(last_po.po_number.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        return f'{prefix}{seq:04d}'

    def recalculate_total(self):
        total = sum(item.line_total for item in self.items.all())
        self.grand_total = total
        self.save(update_fields=['grand_total'])

    def receive_items(self, grn=None):
        from django.apps import apps
        BookCopy = apps.get_model('library_mgmt', 'BookCopy')
        LabUnit = apps.get_model('lab_mgmt', 'LabUnit')

        items_to_process = []
        if grn:
            for grn_item in grn.grn_items.all():
                items_to_process.append({
                    'po_item': grn_item.po_item,
                    'qty': grn_item.quantity_accepted,
                    'item_category': grn_item.po_item.item_category,
                    'linked_book': grn_item.po_item.linked_book,
                    'linked_equipment': grn_item.po_item.linked_equipment
                })
        else:
            for item in self.items.all():
                qty_to_receive = item.quantity - item.received_qty
                if qty_to_receive > 0:
                    items_to_process.append({
                        'po_item': item,
                        'qty': qty_to_receive,
                        'item_category': item.item_category,
                        'linked_book': item.linked_book,
                        'linked_equipment': item.linked_equipment
                    })

        for proc_item in items_to_process:
            qty_to_receive = proc_item['qty']
            if qty_to_receive <= 0:
                continue

            if proc_item['item_category'] == 'book' and proc_item['linked_book']:
                last_copy = BookCopy.objects.order_by('-accession_number').first()
                start_num = 1001
                if last_copy and last_copy.accession_number.startswith('LIB-BK-'):
                    try:
                        start_num = int(last_copy.accession_number.split('-')[-1]) + 1
                    except ValueError:
                        pass
                for i in range(qty_to_receive):
                    acc_no = f"LIB-BK-{start_num + i:04d}"
                    BookCopy.objects.create(
                        book=proc_item['linked_book'],
                        po_item=proc_item['po_item'],
                        accession_number=acc_no,
                        status='available',
                        condition_status='new',
                        availability=True
                    )

            elif proc_item['item_category'] == 'equipment' and proc_item['linked_equipment']:
                last_unit = LabUnit.objects.order_by('-internal_uid').first()
                start_num = 5001
                if last_unit and last_unit.internal_uid.startswith('LAB-EQ-'):
                    try:
                        start_num = int(last_unit.internal_uid.split('-')[-1]) + 1
                    except ValueError:
                        pass
                for i in range(qty_to_receive):
                    uid = f"LAB-EQ-{start_num + i:04d}"
                    LabUnit.objects.create(
                        equipment=proc_item['linked_equipment'],
                        po_item=proc_item['po_item'],
                        internal_uid=uid,
                        status='available'
                    )

            proc_item['po_item'].received_qty += qty_to_receive
            proc_item['po_item'].save(update_fields=['received_qty'])


class PurchaseOrderItem(models.Model):
    ITEM_CATEGORY_CHOICES = [
        ('book', 'Book'),
        ('equipment', 'Lab Equipment'),
        ('consumable', 'Consumable'),
    ]
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item_category = models.CharField(max_length=20, choices=ITEM_CATEGORY_CHOICES)
    item_name = models.CharField(max_length=300, help_text='Title of book or name of equipment')
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1, help_text='Number of units being purchased')
    received_qty = models.PositiveIntegerField(default=0, help_text='Quantity verified upon arrival')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    linked_book = models.ForeignKey(
        'library_mgmt.Book', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='po_items', help_text='Link to existing Book (for type=book)'
    )
    linked_equipment = models.ForeignKey(
        'lab_mgmt.Equipment', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='po_items', help_text='Link to existing Equipment (for type=equipment)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.item_name} x{self.quantity} ({self.get_item_category_display()})"

    @property
    def line_total(self):
        subtotal = self.quantity * self.unit_price
        tax = subtotal * (self.tax_percentage / 100)
        return subtotal + tax

    @property
    def is_fully_received(self):
        return self.received_qty >= self.quantity


class GoodsReceivedNote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('inspected', 'Inspected'),
    ]
    grn_number = models.CharField(max_length=64, unique=True, verbose_name='GRN Number')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='grns')
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='grns_received')
    received_date = models.DateTimeField(default=timezone.now)
    delivery_challan_no = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_date']
        verbose_name = 'Goods Received Note'

    def __str__(self):
        return f"{self.grn_number} ({self.purchase_order.po_number})"

    def save(self, *args, **kwargs):
        if not self.grn_number:
            self.grn_number = self._generate_grn_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_grn_number():
        today = timezone.now().strftime('%Y%m%d')
        prefix = f'GRN-{today}-'
        last_grn = GoodsReceivedNote.objects.filter(grn_number__startswith=prefix).order_by('-grn_number').first()
        if last_grn:
            last_seq = int(last_grn.grn_number.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        return f'{prefix}{seq:04d}'


class GRNItem(models.Model):
    grn = models.ForeignKey(GoodsReceivedNote, on_delete=models.CASCADE, related_name='grn_items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='grn_items')
    quantity_received = models.PositiveIntegerField(default=0)
    quantity_accepted = models.PositiveIntegerField(default=0)
    quantity_rejected = models.PositiveIntegerField(default=0)
    remarks = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.po_item.item_name} (GRN: {self.grn.grn_number})"


class GoodsReturn(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Vendor'),
        ('credited', 'Credit Received'),
    ]
    return_number = models.CharField(max_length=64, unique=True, verbose_name='Return Number')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='returns')
    grn = models.ForeignKey(GoodsReceivedNote, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='returns')
    returned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='returns_made')
    return_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-return_date']

    def __str__(self):
        return self.return_number

    def save(self, *args, **kwargs):
        if not self.return_number:
            self.return_number = self._generate_return_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_return_number():
        today = timezone.now().strftime('%Y%m%d')
        prefix = f'RET-{today}-'
        last_ret = GoodsReturn.objects.filter(return_number__startswith=prefix).order_by('-return_number').first()
        if last_ret:
            last_seq = int(last_ret.return_number.split('-')[-1])
            seq = last_seq + 1
        else:
            seq = 1
        return f'{prefix}{seq:04d}'


class ReturnItem(models.Model):
    goods_return = models.ForeignKey(GoodsReturn, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='returned_items')
    quantity_returned = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.po_item.item_name} (Ret: {self.goods_return.return_number})"
