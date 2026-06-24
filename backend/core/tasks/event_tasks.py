from core.models import Event,Organization
from core.serializers import EventSerializer
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.services.alerts import check_event_spike
from core.tasks.delete_cache import delete_cache_dashboard
from core.tasks.analytics_tasks import event_analytics
from core.tasks.notification_tasks import send_dashboard_update

import django_rq

User = get_user_model()



def create_event_async(org_id, event_type, event_data, user_id):
    try:
        org = Organization.objects.get(id=org_id)
        user = User.objects.get(id=user_id)  # Fetch the User instance

        event = Event.objects.create(
            organization=org,
            event_type=event_type,
            event_data=event_data,
            user_id=user.id,
        )

        print(f"Event saved for org {org_id}")

        cache_queue = django_rq.get_queue('cache')
        analytics_queue = django_rq.get_queue('analytics')
        notification_queue = django_rq.get_queue('notifications')

        cache_queue.enqueue(
            delete_cache_dashboard,
            org_id
        )

        analytics_queue.enqueue(
            event_analytics
        )

        notification_queue.enqueue(
            send_dashboard_update,
            {
                "id": event.id,
                "event_type": event.event_type,
                "organization": event.organization.name,
                "timestamp": event.timestamp.isoformat(),
            }
        )

        # Clear the cache for the organization's events
        #cache.delete_pattern(f"dashboard:{org_id}:*")
        #delete_cache_dashboard(org_id)

        #check_event_spike(org)
        # -----------------------
        # WebSocket notification
        # -----------------------

        #channel_layer = get_channel_layer()
        #async_to_sync(channel_layer.group_send)(
        #    "  ",
        #    {
        #        "type": "dashboard_message",
        #       "data": {
        #            "id": event.id,
        #            "event_type": event.event_type,
        #            "organization": event.organization.name,
        #            "timestamp": event.timestamp.isoformat(),
        #        }
        #    }
        #)

    except Organization.DoesNotExist:
        print(f"Organization with id {org_id} does not exist. Event not saved.")
    
    except Exception as e:
        print(f"Error saving event for org {org_id}: {str(e)}")
        
