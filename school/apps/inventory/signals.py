from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import GoodsReceivedNote, PurchaseOrder


@receiver(post_save, sender=GoodsReceivedNote)
def handle_grn_finalization(sender, instance, created, **kwargs):
    """Trigger item generation when GRN status is set to 'inspected' or 'received'."""
    if instance.status in ['received', 'inspected']:
        instance.purchase_order.receive_items(grn=instance)


@receiver(post_save, sender=PurchaseOrder)
def handle_po_status_change(sender, instance, created, **kwargs):
    """Legacy trigger for backward compatibility or direct receipt."""
    if instance.status == 'received' and instance.received_date is None:
        instance.received_date = timezone.now().date()
        instance.save(update_fields=['received_date'])
        instance.receive_items()
