from .models import Membership

def get_user_organization(user):
    membership = Membership.objects.filter(user=user).first()
    return membership.organization if membership else None

def get_org_and_validate(user, key):
    try:
        org = Organization.objects.get(api_key=key)
    except Organization.DoesNotExist:
        return None, "Invalid API key"

    is_member = Membership.objects.filter(
        user=user,
        organization=org
    ).exists()

    if not is_member:
        return None, "You are not part of this organization"

    return org, None










