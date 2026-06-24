from django.core.cache import cache

def delete_cache_dashboard(org_id):
    
    cache.delete_pattern(f"dashboard:{org_id}:*")