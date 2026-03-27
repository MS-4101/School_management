import pytest
from django.utils import timezone
from apps.inventory.models import Category, Commodity, Supplier, PurchaseOrder, PurchaseOrderItem
from apps.library_mgmt.models import Book

@pytest.fixture
def inventory_setup(db):
    cat = Category.objects.create(name='General')
    comm = Commodity.objects.create(name='Paper', category=cat, unit='Rim', current_stock=10)
    supp = Supplier.objects.create(name='Vendor A', vendor_code='V001')
    return cat, comm, supp

@pytest.mark.django_db
class TestInventoryModels:
    def test_commodity_stock(self, inventory_setup):
        cat, comm, supp = inventory_setup
        assert comm.current_stock == 10
        assert comm.source_label == '📋 Manual'

    def test_purchase_order_generation(self, inventory_setup):
        cat, comm, supp = inventory_setup
        po = PurchaseOrder.objects.create(supplier=supp)
        assert po.po_number.startswith('PO-')
        assert po.status == 'draft'

    def test_receive_items_logic(self, inventory_setup):
        cat, comm, supp = inventory_setup
        book = Book.objects.create(title='Bio', author='Darwin', isbn='999')
        po = PurchaseOrder.objects.create(supplier=supp)
        item = PurchaseOrderItem.objects.create(
            purchase_order=po, item_category='book', item_name='Bio',
            quantity=2, linked_book=book, unit_price=100
        )

        # Receive items
        po.receive_items()

        from apps.library_mgmt.models import BookCopy
        assert BookCopy.objects.filter(book=book, po_item=item).count() == 2
        item.refresh_from_db()
        assert item.received_qty == 2
