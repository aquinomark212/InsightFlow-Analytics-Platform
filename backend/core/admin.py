from django.contrib import admin
from .models import Organization
from .models import Event

admin.site.register(Organization)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'organization', 'user', 'created_at')
    list_filter = ('event_type', 'organization')
    search_fields = ('event_type', 'metadata')