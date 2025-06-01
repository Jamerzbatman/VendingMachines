from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lead
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Handle both create and update
@receiver(post_save, sender=Lead)
def lead_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "leads_group",
        {
            "type": "lead_changed",
            "message": f"Lead {'added' if created else 'updated'}: {instance.company_name}"
        }
    )

@receiver(post_delete, sender=Lead)
def lead_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "leads_group",
        {
            "type": "lead_changed",
            "message": f"Lead deleted: {instance.company_name}"
        }
    )
