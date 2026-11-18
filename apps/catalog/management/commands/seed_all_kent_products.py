import os
import re
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.catalog.models import Category, Product, ProductImage

class Command(BaseCommand):
    help = 'Seeds all 172 KENT products across all 7 categories from media/products/kent/ folders'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting automated seeding of all 172 KENT products..."))

        # 1. Ensure the 7 official Kent categories exist and are active
        categories_meta = {
            'water-purifiers': {
                'name': 'Water Purifiers',
                'icon': 'bi-droplet-half',
                'description': 'Advanced RO, UV, UF and Gravity water purifiers engineered for healthy and pure drinking water.',
                'sort_order': 1,
            },
            'water-softeners': {
                'name': 'Water Softeners',
                'icon': 'bi-water',
                'description': 'Next-generation automatic water softeners to protect appliances, skin, and hair from hard water.',
                'sort_order': 2,
            },
            'chimneys': {
                'name': 'Chimneys',
                'icon': 'bi-wind',
                'description': 'Filterless auto-clean kitchen chimneys with gesture control and powerful suction.',
                'sort_order': 3,
            },
            'gas-stoves': {
                'name': 'Gas Stoves',
                'icon': 'bi-fire',
                'description': 'Toughened glass top gas stoves and cooktops with high thermal efficiency brass burners.',
                'sort_order': 4,
            },
            'kitchen-appliances': {
                'name': 'Kitchen Appliances',
                'icon': 'bi-egg-fried',
                'description': 'Smart induction cooktops, air fryers, mixers, blenders, and healthy food prep appliances.',
                'sort_order': 5,
            },
            'home-appliances': {
                'name': 'Home Appliances',
                'icon': 'bi-lamp',
                'description': 'High-performance vacuum cleaners, garment steamers, and modern home wellness appliances.',
                'sort_order': 6,
            },
            'new-energy': {
                'name': 'New Energy',
                'icon': 'bi-sun',
                'description': 'Clean energy solutions and green innovations powering sustainable households.',
                'sort_order': 7,
            },
        }

        category_objs = {}
        for slug, meta in categories_meta.items():
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': meta['name'],
                    'icon': meta['icon'],
                    'description': meta['description'],
                    'sort_order': meta['sort_order'],
                    'is_active': True,
                }
            )
            category_objs[slug] = cat

        # 2. Path to media/products/kent
        media_kent_dir = os.path.join(settings.MEDIA_ROOT, 'products', 'kent')
        if not os.path.exists(media_kent_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {media_kent_dir}"))
            return

        folders = sorted(os.listdir(media_kent_dir))
        self.stdout.write(f"Found {len(folders)} folders in {media_kent_dir}")

        def folder_to_title(folder):
            words = folder.split('-')
            capitalized = []
            for w in words:
                if w.lower() == 'kent':
                    capitalized.append('KENT')
                elif w.lower() in ['bldc', 'ac', 'iot', 'uv', 'ro', 'uf', 'tds', 'led', 'mppt', 'ups', 'ss']:
                    capitalized.append(w.upper())
                elif re.match(r'^\d+[lwkg]$', w.lower()):
                    capitalized.append(w.upper())
                elif w.lower() == '2y':
                    capitalized.append('2Y')
                elif w.lower() == 'aio':
                    capitalized.append('AIO')
                elif w.lower() == 'g3':
                    capitalized.append('G3')
                elif w.lower() == 'm1':
                    capitalized.append('M1')
                elif w.lower() == 's1':
                    capitalized.append('S1')
                elif w.lower() == 'h1':
                    capitalized.append('H1')
                elif w.lower() == 'f1':
                    capitalized.append('F1')
                elif w.lower() == 'a5':
                    capitalized.append('A5')
                elif w.lower() == 'r1':
                    capitalized.append('R1')
                else:
                    capitalized.append(w.capitalize())
            title = ' '.join(capitalized)
            if not title.startswith('KENT') and not 'KENT' in title:
                title = f"KENT {title}"
            return title

        def classify_folder(folder):
            f = folder.lower()
            if 'chimney' in f:
                return 'chimneys', 'Filterless Auto-Clean BLDC', Decimal('18990.00'), Decimal('24990.00'), 'Modern Kitchens / Residential Cooking', '1200 m3/hr Suction, Motion Sensor, Touch Control'
            if any(k in f for k in ['softener', 'sand-filter', 'iron-removal', 'autosoft', 'pressure-boosting']):
                return 'water-softeners', 'Automatic Ion-Exchange Resin', Decimal('24990.00'), Decimal('32990.00'), 'Entire Home / Bathroom / Washing Machine', 'Multi-Port Valve, Automatic Regeneration, High Salt Capacity'
            if any(k in f for k in ['gas-stove']):
                return 'gas-stoves', 'High-Efficiency Brass Burners', Decimal('6990.00'), Decimal('9490.00'), 'Residential Kitchen / Everyday Cooking', 'Toughened Glass, Spill-Proof Tray, Ergonomic Knobs'
            if any(k in f for k in ['air-fryer', 'kettle', 'toaster', 'blender', 'mixer', 'cooker', 'egg-boiler', 'grinder', 'juicer', 'bread-maker', 'chopper', 'sandwich', 'induction', 'infrared', 'cooktop', 'vegetable-cleaner', 'rapidmix', 'truemix', 'hot-pot', 'coffee']):
                return 'kitchen-appliances', 'Smart Food Preparation & Heating', Decimal('4490.00'), Decimal('5990.00'), 'Kitchen Countertop / Family Prep', 'Food Grade Material, Overheat Protection, Energy Efficient'
            if any(k in f for k in ['vacuum', 'steamer', 'iron', 'humidifier', 'air-purifier', 'roboklean']):
                return 'home-appliances', 'HEPA Filtration & High-Suction Care', Decimal('8990.00'), Decimal('11990.00'), 'Home Living / Deep Cleaning & Wellness', 'High Airflow, Low Noise Operation, Ergonomic Handling'
            if any(k in f for k in ['solar', 'battery', 'inverter', 'ups', 'all-in-one-aio']):
                return 'new-energy', 'Smart MPPT Solar & Lithium Backup', Decimal('34990.00'), Decimal('44990.00'), 'Home Energy Independence / Rooftop Backup', 'Pure Sine Wave, High Efficiency MPPT, Long Battery Cycle'
            # Default: Water Purifiers
            return 'water-purifiers', 'RO + UV + UF + TDS Control', Decimal('16990.00'), Decimal('19990.00'), 'Home Drinking & Culinary Needs', 'Mineral RO(TM) Technology, In-Tank UV Disinfection, TDS Balancer'

        def extract_capacity(folder):
            m = re.search(r'(\d+(?:\.\d+)?)\s*l\b', folder.lower())
            if m:
                try:
                    return Decimal(m.group(1))
                except Exception:
                    pass
            if 'water-purifiers' in folder.lower():
                return Decimal('8.0')
            return Decimal('0.0')

        seeded_count = 0
        category_counts = {}

        for folder in folders:
            folder_path = os.path.join(media_kent_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            images = sorted([img for img in os.listdir(folder_path) if img.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))])
            cat_slug, tech, price, orig_price, intended_use, stages = classify_folder(folder)
            cat_obj = category_objs[cat_slug]
            title = folder_to_title(folder)
            capacity = extract_capacity(folder)

            primary_img_rel = f"products/kent/{folder}/{images[0]}" if images else None

            # Generate realistic features
            features = [
                f"Engineered with premium {tech} for optimal everyday performance.",
                f"Designed for {intended_use}.",
                "Backed by KENT House of Purity manufacturing standards and responsive Pan-India customer support."
            ]

            specifications = {
                'Brand': 'KENT',
                'Technology': tech,
                'Model': title,
                'Intended Use': intended_use,
                'Warranty': '1 Year Comprehensive Manufacturer Warranty',
                'Installation': 'Standard installation supported across India',
            }
            if capacity > 0:
                specifications['Capacity'] = f"{capacity} Liters"

            # Check if product exists
            prod_obj, created = Product.objects.update_or_create(
                slug=folder,
                defaults={
                    'name': title,
                    'brand': 'KENT',
                    'category': cat_obj,
                    'short_description': f"{title} featuring {tech} for modern Indian households.",
                    'description': (
                        f"Experience exceptional performance with {title}. Built to exacting KENT quality standards, "
                        f"this appliance integrates {tech} with durable food-grade components, ensuring maximum efficiency, "
                        f"safety, and enduring reliability for your everyday home needs."
                    ),
                    'technology': tech,
                    'storage_capacity_liters': capacity,
                    'price': price,
                    'original_price': orig_price,
                    'image': primary_img_rel,
                    'image_alt_text': f"{title} - Official Image",
                    'purification_stages': stages,
                    'intended_use': intended_use,
                    'features': features,
                    'specifications': specifications,
                    'stock_quantity': 25,
                    'status': 'published',
                    'is_active': True,
                    'is_featured': (seeded_count % 15 == 0),
                }
            )

            # Sync gallery images
            if images:
                prod_obj.images.all().delete()
                for idx, img_file in enumerate(images, start=1):
                    rel_img = f"products/kent/{folder}/{img_file}"
                    ProductImage.objects.create(
                        product=prod_obj,
                        image=rel_img,
                        alt_text=f"{title} - View {idx}",
                        is_primary=(idx == 1),
                        display_order=idx
                    )

            seeded_count += 1
            category_counts[cat_slug] = category_counts.get(cat_slug, 0) + 1

        self.stdout.write(self.style.SUCCESS(f"\n[SUCCESS] Successfully seeded {seeded_count} products across all categories!"))
        for cat_slug, count in sorted(category_counts.items()):
            self.stdout.write(self.style.SUCCESS(f"  - {categories_meta[cat_slug]['name']}: {count} products"))
