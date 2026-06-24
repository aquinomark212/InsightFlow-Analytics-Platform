from core.services.alerts import check_event_spike
from core.models import Organization


def event_analytics(org_id):
     
     org = Organization.objects.get(id=org_id)

     check_event_spike(org)
