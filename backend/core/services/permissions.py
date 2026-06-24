from .core.Membership.models import Membership

def has_access(user, org_id):
    return Membership.objects.filter(
        user=user,
        organization_id=org_id
    ).exists()

def get_user_permissions(user, org_id):
    membership = Membership.objects.filter(
        user=user,
        organization_id=org_id
    ).first()

    if not membership:
        return None

    return membership.role