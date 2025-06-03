from django.db.models.signals import post_save, post_delete
from channels.layers import get_channel_layer
from django.utils.timezone import make_aware
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from datetime import datetime
from .models import Lead

# Helper function to count today's leads
def get_today_leads_count(source):
    today = make_aware(datetime.now()).date()
    return Lead.objects.filter(source=source, created_at__date=today).count()

@receiver(post_save, sender=Lead)
def lead_saved(sender, instance, created, **kwargs):
    # Get today's lead counts for 'website' and 'ai' sources
    website_leads = get_today_leads_count('website')
    ai_leads = get_today_leads_count('ai')
    total_leads = Lead.objects.count()

    # Send the updated lead counts to WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "website_leads": website_leads,
            "ai_leads": ai_leads,
            "total_leads": total_leads,
            "message": f"Lead {'added' if created else 'updated'}: {instance.company_name}"
        }
    )
    async_to_sync(channel_layer.group_send)(
        "dashboard_leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "website_leads": website_leads,
            "ai_leads": ai_leads,
            "total_leads": total_leads,
            "message": f"Lead {'added' if created else 'updated'}: {instance.company_name}"
        }
    )
    async_to_sync(channel_layer.group_send)(
        "sidebar_leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "total_leads": total_leads,
            "message": f"Lead {'added' if created else 'updated'}: {instance.company_name}"
        }
    )


@receiver(post_delete, sender=Lead)
def lead_deleted(sender, instance, **kwargs):
    # Get today's lead counts for 'website' and 'ai' sources after deletion
    website_leads = get_today_leads_count('website')
    ai_leads = get_today_leads_count('ai')
    total_leads = Lead.objects.count()
    # Send the updated lead counts to WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "website_leads": website_leads,
            "ai_leads": ai_leads,
            "total_leads": total_leads,
            "message": f"Lead deleted: {instance.company_name}"

        }
    )
    async_to_sync(channel_layer.group_send)(
        "dashboard_leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "website_leads": website_leads,
            "ai_leads": ai_leads,
            "total_leads": total_leads,
            "message": f"Lead deleted: {instance.company_name}"
        }
    )
    async_to_sync(channel_layer.group_send)(
        "sidebar_leads_group",  # The group name
        {
            "type": "lead_changed",  # Event type
            "total_leads": total_leads,
            "message": f"Lead deleted: {instance.company_name}"
        }
    )

