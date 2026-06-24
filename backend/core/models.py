from django.db import models
from django.contrib.auth.models import User   # ← Import this!
from django.conf import settings
from django.utils import timezone
import uuid


class Organization(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, null=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} - {self.role}"


class Event(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=255)
    event_data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.organization.name} - {self.created_at}"

class Alert(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    message = models.TextField()
    alert_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

