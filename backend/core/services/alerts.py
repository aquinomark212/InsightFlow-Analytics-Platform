from django.test import TestCase
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta

# Create your tests here.
def check_event_spike(org):
    from core.models import Event

    Spike_THRESHOLD = 10  # Example threshold for spike detection

    one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)

    last_minute_count = Event.objects.filter(
        organization=org,
        timestamp__gte=one_minute_ago
    ).count()

    if last_minute_count > Spike_THRESHOLD:
        print(f"Spike detected for org {org.name}: {last_minute_count} events in the last minute")

        send_alert(org, last_minute_count)


def send_alert(org, count):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "dashboard",
        {
            "type": "send_alert",
            "data": {
                "message": f"🚨 Spike detected! {count} events in the last minute.",
                "alert_type": "spike"
            }
        }
    )
