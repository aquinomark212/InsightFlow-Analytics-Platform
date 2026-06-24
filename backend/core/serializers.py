from rest_framework import serializers
from django.contrib.auth.models import User  
from .models import Organization, Membership, Event

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'organization_name']

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name')

        user = User.objects.create_user(**validated_data)
        organization = Organization.objects.create(
            name=org_name,
            owner=user
            )

        Membership.objects.create(
            user=user,
            organization=organization,
            role='admin'
        )

        return user

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'organization', 'user', 'event_type', 'event_data', 'created_at']
        read_only_fields = ['created_at']


