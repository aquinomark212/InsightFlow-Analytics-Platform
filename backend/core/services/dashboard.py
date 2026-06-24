from django.db.models import Count
from django.db.models.functions import TruncDate
from ..models import Event
from django.utils import timezone
from datetime import datetime, time

def apply_date_filter(queryset, start_date=None, end_date=None):
    if start_date:
        start_dt = timezone.make_aware(
            datetime.combine(start_date, time.min)
        )
        queryset = queryset.filter(timestamp__gte=start_dt)

    if end_date:
        end_dt = timezone.make_aware(
            datetime.combine(end_date, time.max)
        )
        queryset = queryset.filter(timestamp__lte=end_dt)

    return queryset

def get_total_events(org, start_date=None, end_date=None):
    qs = Event.objects.filter(organization=org)
    qs = apply_date_filter(qs, start_date, end_date)
    return qs.count()

def get_events_per_day(org, start_date=None, end_date=None):
    qs = Event.objects.filter(organization=org)
    qs = apply_date_filter(qs, start_date, end_date)


    return list(
        qs
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date') 
    )

def get_top_event_types(org, start_date=None, end_date=None):
    qs = Event.objects.filter(organization=org)
    qs = apply_date_filter(qs, start_date, end_date)
    return list(
        qs
        .values('event_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

def get_recent_events(org, start_date=None, end_date=None, limit=10):
    qs = Event.objects.filter(organization=org)
    qs = apply_date_filter(qs, start_date, end_date)

    return list(
        qs
        .order_by('-timestamp')
        .values('id', 'event_type', 'timestamp')[:limit]
    )

