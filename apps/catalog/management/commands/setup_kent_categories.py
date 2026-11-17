from django.core.management.base import BaseCommand
from apps.catalog.models import Category

class Command(BaseCommand):
    help = 'Sets up the official 7 Kent product categories and deactivates legacy subcategories for clean navigation.'

    def handle(self, *args, **options):
        official_categories = [
            {
                'name': 'Water Purifiers',
                'slug': 'water-purifiers',
                'icon': 'bi-droplet-half',
                'description': 'Advanced RO, UV, UF and Gravity water purifiers engineered for healthy and pure drinking water.',
                'sort_order': 1,
                'is_active': True,
            },
            {
                'name': 'Water Softeners',
                'slug': 'water-softeners',
                'icon': 'bi-water',
                'description': 'Next-generation automatic water softeners to protect appliances, skin, and hair from hard water.',
                'sort_order': 2,
                'is_active': True,
            },
            {
                'name': 'Chimneys',
                'slug': 'chimneys',
                'icon': 'bi-wind',
                'description': 'Filterless auto-clean kitchen chimneys with gesture control and powerful suction.',
                'sort_order': 3,
                'is_active': True,
            },
            {
                'name': 'Gas Stoves',
                'slug': 'gas-stoves',
                'icon': 'bi-fire',
                'description': 'Toughened glass top gas stoves and cooktops with high thermal efficiency brass burners.',
                'sort_order': 4,
                'is_active': True,
            },
            {
                'name': 'Kitchen Appliances',
                'slug': 'kitchen-appliances',
                'icon': 'bi-egg-fried',
                'description': 'Smart induction cooktops, air fryers, mixers, blenders, and healthy food prep appliances.',
                'sort_order': 5,
                'is_active': True,
            },
            {
                'name': 'Home Appliances',
                'slug': 'home-appliances',
                'icon': 'bi-lamp',
                'description': 'High-performance vacuum cleaners, garment steamers, and modern home wellness appliances.',
                'sort_order': 6,
                'is_active': True,
            },
            {
                'name': 'New Energy',
                'slug': 'new-energy',
                'icon': 'bi-sun',
                'description': 'Clean energy solutions and green innovations powering sustainable households.',
                'sort_order': 7,
                'is_active': True,
            },
        ]

        active_slugs = set()
        for cat in official_categories:
            slug = cat['slug']
            active_slugs.add(slug)
            obj, created = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': cat['name'],
                    'icon': cat['icon'],
                    'description': cat['description'],
                    'sort_order': cat['sort_order'],
                    'is_active': True,
                }
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"[OK] {action} category: {obj.name} ({obj.slug})"))

        # Deactivate any other legacy categories so only the 7 official Kent categories appear in nav
        legacy = Category.objects.exclude(slug__in=active_slugs)
        count = legacy.update(is_active=False)
        self.stdout.write(self.style.NOTICE(f"[INFO] Deactivated {count} legacy subcategories from top navigation (products remain linked and accessible via slug_aliases)."))
