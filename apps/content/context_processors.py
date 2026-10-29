from apps.content.models import SiteSetting
from apps.catalog.models import Category

def site_context(request):
    """Provides site settings, active categories, and brand data to all templates."""
    try:
        site_settings = SiteSetting.load()
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    except Exception:
        site_settings = None
        categories = []

    return {
        'site_settings': site_settings,
        'nav_categories': categories,
        'BRAND_NAME': 'AQUAVERA',
        'BRAND_TAGLINE': 'Pure Water. Thoughtfully Designed.',
    }
