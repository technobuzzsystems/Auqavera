import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser
from apps.catalog.models import Category, Product, ProductImage
from apps.content.models import Testimonial, FAQ, SiteSetting
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest

class Command(BaseCommand):
    help = 'Seeds initial demo categories, fictional products, FAQs, testimonials, and sample records.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Initializing AQUAVERA demo database seeding..."))

        # 1. Site Settings
        setting, _ = SiteSetting.objects.get_or_create(id=1)
        setting.website_name = "AQUAVERA"
        setting.tagline = "Pure Water. Thoughtfully Designed."
        setting.support_email = "support@aquavera.com"
        setting.support_phone = "+91 1800 200 4567"
        setting.address = "AQUAVERA Water Innovation Center, Sector 62, Noida, NCR 201309"
        setting.announcement_text = "Discover smarter multi-stage water purification for modern homes."
        setting.social_links = {
            'facebook': 'https://facebook.com',
            'instagram': 'https://instagram.com',
            'twitter': 'https://x.com',
            'linkedin': 'https://linkedin.com'
        }
        setting.save()
        self.stdout.write(self.style.SUCCESS("[OK] Site settings configured."))

        # 2. Categories
        categories_data = [
            {
                'name': 'RO Water Purifiers',
                'slug': 'ro-water-purifiers',
                'icon': 'bi-droplet-half',
                'description': 'Advanced Reverse Osmosis filtration systems engineered for high TDS, borewell, and mixed municipal water sources.',
                'sort_order': 1,
            },
            {
                'name': 'UV Water Purifiers',
                'slug': 'uv-water-purifiers',
                'icon': 'bi-sun',
                'description': 'High-intensity ultraviolet disinfection systems designed for tap and municipal water with low dissolved solids.',
                'sort_order': 2,
            },
            {
                'name': 'UF Water Purifiers',
                'slug': 'uf-water-purifiers',
                'icon': 'bi-shield-check',
                'description': 'Ultrafiltration hollow-fiber barrier technology eliminating physical impurities and bacteria without electricity.',
                'sort_order': 3,
            },
            {
                'name': 'Gravity Water Purifiers',
                'slug': 'gravity-water-purifiers',
                'icon': 'bi-layers',
                'description': 'Non-electric, gravity-fed purifiers featuring multi-stage carbon and ceramic filtration for easy everyday use.',
                'sort_order': 4,
            },
            {
                'name': 'Commercial Water Purifiers',
                'slug': 'commercial-water-purifiers',
                'icon': 'bi-building',
                'description': 'Heavy-duty high-flow commercial water filtration systems for offices, cafes, clinics, and educational campuses.',
                'sort_order': 5,
            },
        ]

        cat_objs = {}
        for c in categories_data:
            obj, created = Category.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'name': c['name'],
                    'icon': c['icon'],
                    'description': c['description'],
                    'sort_order': c['sort_order'],
                    'is_active': True,
                }
            )
            cat_objs[c['slug']] = obj
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cat_objs)} Product categories seeded."))

        # 3. Products (10 Fictional, Realistic Demo Purifiers)
        products_data = [
            {
                'name': 'AQUAVERA Crystal Optima RO',
                'slug': 'aquavera-crystal-optima-ro',
                'category': cat_objs['ro-water-purifiers'],
                'short_description': 'Flagship 7-stage RO purifier with digital TDS balancer and mineralizer.',
                'description': 'The AQUAVERA Crystal Optima RO combines high-rejection thin-film composite membrane filtration with ultraviolet germicidal disinfection and natural mineral restoration. Engineered specifically for complex residential water sources with TDS up to 2000 ppm.',
                'technology': 'RO + UV + UF + TDS Control',
                'storage_capacity_liters': Decimal('9.0'),
                'price': Decimal('16990.00'),
                'original_price': Decimal('19990.00'),
                'purification_stages': '7 Stages: Polypropylene Spun, Dual Carbon Block, RO Membrane, UV Disinfection, Post Carbon, Mineralizer, Copper Infusion',
                'intended_use': 'Home / Borewell & Municipal Tap Water (TDS < 2000)',
                'maintenance_information': 'Sediment and carbon cartridge exchange every 6 months. High-durability RO membrane service interval: 18-24 months.',
                'specifications': {
                    'Filtration Rate': '15 Liters/Hour',
                    'Tank Material': 'Food Grade ABS Antibacterial Plastic',
                    'Input Voltage': '100 - 240V AC, 50-60Hz',
                    'Power Consumption': '60 Watts',
                    'Mounting': 'Wall Mounted or Countertop',
                    'Dimensions': '390 x 275 x 520 mm',
                    'Net Weight': '8.6 kg',
                },
                'is_featured': True,
            },
            {
                'name': 'AQUAVERA PureFlow Smart RO',
                'slug': 'aquavera-pureflow-smart-ro',
                'category': cat_objs['ro-water-purifiers'],
                'short_description': 'Intelligent 8-stage purifier featuring real-time water quality monitoring.',
                'description': 'The PureFlow Smart RO introduces dual-sensor TDS monitoring and active auto-flush technology that prolongs membrane lifespan. Features a sleek touch-dispense panel and quiet booster pump for low-pressure apartments.',
                'technology': 'Smart RO + UV + Alkaline + Mineralizer',
                'storage_capacity_liters': Decimal('10.0'),
                'price': Decimal('21490.00'),
                'original_price': Decimal('24990.00'),
                'purification_stages': '8 Stages: Pre-Filter, Sediment Core, Granular Carbon, RO High Rejection, In-Tank UV LED, Post-Carbon, Alkaline Balancer, Bioceramic Ring',
                'intended_use': 'Modern Apartments, High TDS & Mixed Tanker Water',
                'maintenance_information': 'Smart filter life indicator alerts users. Recommended filter swap at 6000 liters or 12 months.',
                'specifications': {
                    'Filtration Rate': '18 Liters/Hour',
                    'Tank Material': 'UV-Shielded Food Grade ABS',
                    'Input Voltage': '160 - 260V AC',
                    'Power Consumption': '65 Watts',
                    'Mounting': 'Wall Mounted',
                    'Dimensions': '405 x 290 x 535 mm',
                    'Net Weight': '9.2 kg',
                },
                'is_featured': True,
            },
            {
                'name': 'AQUAVERA HydroShield Compact RO',
                'slug': 'aquavera-hydroshield-compact-ro',
                'category': cat_objs['ro-water-purifiers'],
                'short_description': 'Space-saving slimline RO water purifier designed for compact kitchen setups.',
                'description': 'Delivers uncompromised multi-stage reverse osmosis in a slender 250mm chassis. Ideal for nuclear families seeking dependable purification without sacrificing kitchen wall real estate.',
                'technology': 'RO + UV + Active Carbon',
                'storage_capacity_liters': Decimal('7.0'),
                'price': Decimal('13490.00'),
                'original_price': Decimal('15990.00'),
                'purification_stages': '6 Stages: Sediment, Carbon Block, Micro-mesh, RO Membrane, UV Disinfection, Odor Eliminator',
                'intended_use': '1-3 Member Households / Urban Kitchens',
                'maintenance_information': 'Quarterly checkup recommended; standard 10-inch filter cartridge replacements readily available.',
                'specifications': {
                    'Filtration Rate': '12 Liters/Hour',
                    'Tank Material': 'Food Grade ABS',
                    'Power Consumption': '48 Watts',
                    'Mounting': 'Wall Mounted or Shelf',
                    'Dimensions': '340 x 245 x 480 mm',
                    'Net Weight': '7.4 kg',
                },
                'is_featured': False,
            },
            {
                'name': 'AQUAVERA Lumina UV Active',
                'slug': 'aquavera-lumina-uv-active',
                'category': cat_objs['uv-water-purifiers'],
                'short_description': 'High-flow UV disinfection purifier with stainless steel purification chamber.',
                'description': 'Designed specifically for clean municipal tap water sources (TDS < 250 ppm) where microbial protection and mineral retention are desired. Utilizes an 11W Phillips UV lamp housed in a medical-grade 304 stainless steel chamber.',
                'technology': 'UV + UF Dual Disinfection',
                'storage_capacity_liters': Decimal('7.5'),
                'price': Decimal('9490.00'),
                'original_price': Decimal('11290.00'),
                'purification_stages': '5 Stages: Micron Sediment Filter, Activated Carbon Block, Hollow UF Barrier, High-Power UV Chamber, Silver Impregnated Post-Carbon',
                'intended_use': 'Municipal Tap Water / Low TDS Sources',
                'maintenance_information': 'Annual UV lamp inspection; replace carbon cartridge every 6-9 months.',
                'specifications': {
                    'Filtration Rate': '60 Liters/Hour (Fast Direct Flow)',
                    'Chamber Material': 'SS 304 Surgical Grade Stainless Steel',
                    'Power Consumption': '25 Watts',
                    'Mounting': 'Wall Mounted',
                    'Dimensions': '360 x 260 x 460 mm',
                    'Net Weight': '6.1 kg',
                },
                'is_featured': True,
            },
            {
                'name': 'AQUAVERA RayGuard UV Express',
                'slug': 'aquavera-rayguard-uv-express',
                'category': cat_objs['uv-water-purifiers'],
                'short_description': 'Instant on-demand UV purifier with zero water wastage.',
                'description': 'Zero water discharge technology ensures 100% of the incoming municipal water is purified instantly. Features auto shut-off failsafe that blocks water flow if the UV lamp fails.',
                'technology': 'UV + Sediment + Carbon Block',
                'storage_capacity_liters': Decimal('8.0'),
                'price': Decimal('8290.00'),
                'original_price': Decimal('9990.00'),
                'purification_stages': '4 Stages: High-Flow Sediment, Bacteriostatic Carbon, High-Intensity UV Chamber, Mineral Guard',
                'intended_use': 'Municipal Water / Zero Wastage Homes',
                'maintenance_information': 'Filter kit replacement recommended every 12 months.',
                'specifications': {
                    'Filtration Rate': '50 Liters/Hour',
                    'Tank Material': 'Food Grade Polymer',
                    'Power Consumption': '22 Watts',
                    'Mounting': 'Wall Mounted',
                    'Dimensions': '345 x 250 x 450 mm',
                    'Net Weight': '5.8 kg',
                },
                'is_featured': False,
            },
            {
                'name': 'AQUAVERA UltraPure Flow UF',
                'slug': 'aquavera-ultrapure-flow-uf',
                'category': cat_objs['uf-water-purifiers'],
                'short_description': 'Non-electric hollow-fiber ultrafiltration purifier.',
                'description': 'Harnesses 0.01 micron ultrafiltration hollow fiber membranes to block cysts, bacteria, and micro-particles without requiring electrical power or chemical additives.',
                'technology': 'Gravity Hollow Fiber UF + Carbon',
                'storage_capacity_liters': Decimal('8.5'),
                'price': Decimal('6490.00'),
                'original_price': Decimal('7990.00'),
                'purification_stages': '3 Stages: Spun Sediment, Micro-Carbon Block, 0.01 Micron UF Membrane',
                'intended_use': 'Low TDS Municipal Supply / Power Cut Resilient',
                'maintenance_information': 'Washable UF membrane; forward flush once every 2 weeks.',
                'specifications': {
                    'Filtration Rate': '20 Liters/Hour',
                    'Tank Material': 'BPA-Free Food Grade SAN',
                    'Power Consumption': '0 Watts (Non-Electric)',
                    'Mounting': 'Tabletop / Countertop',
                    'Dimensions': '320 x 280 x 490 mm',
                    'Net Weight': '4.5 kg',
                },
                'is_featured': False,
            },
            {
                'name': 'AQUAVERA ClearStream Ultra UF',
                'slug': 'aquavera-clearstream-ultra-uf',
                'category': cat_objs['uf-water-purifiers'],
                'short_description': 'High-capacity gravity storage ultrafiltration unit.',
                'description': 'Combines a dual-chamber gravity reservoir with micro-porous carbon adsorption. Delivers clean, crystal-clear drinking water even in areas with irregular electricity supply.',
                'technology': 'UF + Activated Carbon Block',
                'storage_capacity_liters': Decimal('9.0'),
                'price': Decimal('7190.00'),
                'original_price': Decimal('8490.00'),
                'purification_stages': '4 Stages: Micro-Sediment, Activated Coconut Carbon, 0.01 Micron UF, Mineral Polisher',
                'intended_use': 'Apartments with reliable low TDS water',
                'maintenance_information': 'Annual cartridge package replacement.',
                'specifications': {
                    'Filtration Rate': '18 Liters/Hour',
                    'Tank Material': 'BPA-Free Translucent Food Grade Tank',
                    'Power Consumption': '0 Watts',
                    'Mounting': 'Countertop',
                    'Dimensions': '330 x 290 x 510 mm',
                    'Net Weight': '4.8 kg',
                },
                'is_featured': False,
            },
            {
                'name': 'AQUAVERA TerraGravity Natura',
                'slug': 'aquavera-terragravity-natura',
                'category': cat_objs['gravity-water-purifiers'],
                'short_description': 'Non-electric natural ceramic and activated carbon gravity purifier.',
                'description': 'Features a diatomaceous micro-ceramic filtration candle that physically filters bacteria, protozoa, and suspended particles. Operates purely by gravitational pressure.',
                'technology': 'Gravity Micro-Ceramic + Carbon',
                'storage_capacity_liters': Decimal('14.0'),
                'price': Decimal('3490.00'),
                'original_price': Decimal('4290.00'),
                'purification_stages': '3 Stages: 0.2 Micron Ceramic Candle, Granular Coconut Carbon, Silver Ion Sanitizer',
                'intended_use': 'Budget-conscious homes, rural residences, emergency prep',
                'maintenance_information': 'Scrub ceramic candle with soft pad monthly; replace candle annually.',
                'specifications': {
                    'Filtration Rate': '4 Liters/Hour',
                    'Tank Capacity': '14 Liters (Raw: 6L, Pure: 8L)',
                    'Material': 'Durable BPA-Free Polymer',
                    'Power Consumption': '0 Watts',
                    'Mounting': 'Countertop',
                    'Dimensions': '310 x 310 x 570 mm',
                    'Net Weight': '3.2 kg',
                },
                'is_featured': False,
            },
            {
                'name': 'AQUAVERA Titan Commercial 50 LPH',
                'slug': 'aquavera-titan-commercial-50-lph',
                'category': cat_objs['commercial-water-purifiers'],
                'short_description': 'High-flow commercial reverse osmosis plant with 50 Liters/Hour capacity.',
                'description': 'Designed for bustling commercial spaces, corporate pantries, schools, and boutique cafes. Equipped with dual commercial-grade RO membranes and a heavy-duty rotary vane pump.',
                'technology': 'High-Flow Commercial RO + Dual Sediment + Carbon',
                'storage_capacity_liters': Decimal('25.0'),
                'price': Decimal('38990.00'),
                'original_price': Decimal('45000.00'),
                'purification_stages': '6 Stages: 20-inch Jumbo Sediment, Carbon Block, Anti-Scalant Dosing, Twin 150 GPD RO Membranes, Post-Carbon, Auto-Flush Controller',
                'intended_use': 'Offices (25-70 people), Cafes, Clinics, Restaurants',
                'maintenance_information': 'Quarterly preventive maintenance visits; pre-filters replaced every 3 months in commercial usage.',
                'specifications': {
                    'Filtration Rate': '50 Liters/Hour',
                    'Storage': '25 Liter External Pressure Tank compatible',
                    'Booster Pump': '300 GPD Heavy-duty diaphragm',
                    'Power Consumption': '120 Watts',
                    'Mounting': 'Floor Skid / Wall Mountable',
                    'Dimensions': '500 x 320 x 780 mm',
                    'Net Weight': '18.5 kg',
                },
                'is_featured': True,
            },
            {
                'name': 'AQUAVERA Enterprise Pro 100 LPH',
                'slug': 'aquavera-enterprise-pro-100-lph',
                'category': cat_objs['commercial-water-purifiers'],
                'short_description': 'Industrial-grade continuous purification station for high-footfall institutions.',
                'description': 'Our largest turnkey purification solution featuring automated digital salinity controllers, dual pressure gauges, and stainless steel skid frame for uninterrupted round-the-clock purity.',
                'technology': 'Twin Membrane Industrial RO + UV Sterilizer',
                'storage_capacity_liters': Decimal('50.0'),
                'price': Decimal('64990.00'),
                'original_price': Decimal('75000.00'),
                'purification_stages': '7 Stages: 20-inch Spun Cartridge, Dual Acid-Washed Carbon, High-Pressure RO Membranes, UV Disinfection Tower, Polishing Carbon, Mineralizer',
                'intended_use': 'Offices (75-200 people), Co-working Hubs, Gyms, Clinics',
                'maintenance_information': 'Bimonthly scheduled maintenance contract; real-time pressure monitoring alerts.',
                'specifications': {
                    'Filtration Rate': '100 Liters/Hour',
                    'Storage Tank': '50L Food Grade Sanitized Reservoir Included',
                    'Booster Pump': 'Industrial High-Pressure Pump',
                    'Power Consumption': '250 Watts',
                    'Frame': 'Powder Coated Stainless Steel Skid',
                    'Dimensions': '650 x 420 x 950 mm',
                    'Net Weight': '28.0 kg',
                },
                'is_featured': False,
            },
        ]

        image_mapping = {
            "aquavera-crystal-optima-ro": "products/gallery/AQUAVERA_Premium_Water_Purifier.png",
            "aquavera-pureflow-smart-ro": "products/gallery/AQUAVERA_Smart_Water_Purifier.png",
            "aquavera-hydroshield-compact-ro": "products/gallery/AQUAVERA_Advanced_Water_Purifier.png",
            "aquavera-lumina-uv-active": "products/gallery/Aquavera_Pure_Water_Purifier_System.png",
            "aquavera-rayguard-uv-express": "products/gallery/Aqua_Grand_Plus.webp",
            "aquavera-ultrapure-flow-uf": "products/gallery/AQUAVERA_Advanced_Water_Purifier.png",
            "aquavera-clearstream-ultra-uf": "products/gallery/AQUAVERA_Premium_Water_Purifier.png",
            "aquavera-terragravity-natura": "products/gallery/Aquavera_Pure_Water_Purifier_System.png",
            "aquavera-titan-commercial-50-lph": "products/gallery/Aqua_Grand_Plus.webp",
            "aquavera-enterprise-pro-100-lph": "products/gallery/AQUAVERA_Smart_Water_Purifier.png",
        }
        gallery_extras = [
            "products/gallery/angle_front.jpg",
            "products/gallery/side_view.jpg",
            "products/gallery/filter_view.jpg",
        ]

        for p in products_data:
            img_path = image_mapping.get(p['slug'], "products/gallery/AQUAVERA_Premium_Water_Purifier.png")
            prod_defaults = dict(p)
            prod_defaults['image'] = img_path
            prod_obj, _ = Product.objects.update_or_create(
                slug=p['slug'],
                defaults=prod_defaults
            )
            if not prod_obj.images.exists():
                ProductImage.objects.create(
                    product=prod_obj,
                    image=img_path,
                    alt_text=f"{prod_obj.name} - Front View",
                    is_primary=True,
                    display_order=1
                )
                for idx, extra in enumerate(gallery_extras, start=2):
                    ProductImage.objects.create(
                        product=prod_obj,
                        image=extra,
                        alt_text=f"{prod_obj.name} - View {idx}",
                        is_primary=False,
                        display_order=idx
                    )
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(products_data)} Water Purifiers seeded with gallery images."))


        # 4. Clearly Marked Demo Testimonials
        testimonials_data = [
            {
                'display_name': 'Rohan Deshmukh',
                'city': 'Pune, Maharashtra',
                'designation': 'Software Architect',
                'content': 'We recently tested the Crystal Optima RO unit for our municipal mixed supply. The water taste is consistently crisp, and the maintenance alerts make filter upkeep completely effortless.',
                'rating': 5,
                'is_demo_content': True,
                'is_active': True,
            },
            {
                'display_name': 'Pooja Venkatesh',
                'city': 'Bengaluru, Karnataka',
                'designation': 'Interior Consultant',
                'content': 'The compact aesthetic of the PureFlow Smart fits seamlessly into our modular kitchen. Unlike bulky purifiers, the thoughtful design and responsive technician support stand out.',
                'rating': 5,
                'is_demo_content': True,
                'is_active': True,
            },
            {
                'display_name': 'Arun Verma',
                'city': 'Gurugram, NCR',
                'designation': 'Operations Manager, Co-Work Studio',
                'content': 'Our coworking office uses the Titan Commercial 50 LPH model. Even during peak working hours, drinking water flow never slows down and the team has had zero complaints.',
                'rating': 5,
                'is_demo_content': True,
                'is_active': True,
            },
        ]

        for t in testimonials_data:
            Testimonial.objects.update_or_create(
                display_name=t['display_name'],
                defaults=t
            )
        self.stdout.write(self.style.SUCCESS("[OK] 3 Demo Testimonials seeded."))

        # 5. FAQs
        faqs_data = [
            {
                'category': 'technology',
                'sort_order': 1,
                'question': 'How do I know whether I need an RO or UV water purifier?',
                'answer': 'Your water source total dissolved solids (TDS) level dictates the technology. If your TDS is above 300 ppm (typical for borewell or tanker water), RO is recommended to remove heavy metals and excess hardness. For tap or municipal water below 250 ppm, a UV or UF purifier provides optimal microbial disinfection while preserving beneficial natural minerals.',
            },
            {
                'category': 'technology',
                'sort_order': 2,
                'question': 'What is TDS Control / Mineralizer technology?',
                'answer': 'Reverse Osmosis can remove both harmful contaminants and healthy dissolved minerals. AQUAVERA TDS Control and Mineralizer technology dynamically rebalances essential minerals such as Calcium and Magnesium to ensure sweet-tasting, wholesome drinking water.',
            },
            {
                'category': 'maintenance',
                'sort_order': 3,
                'question': 'How often do filters and RO membranes need to be replaced?',
                'answer': 'Pre-sediment and carbon block filters typically require replacement every 6 months depending on sediment load. High-rejection RO membranes generally last 18 to 24 months. AQUAVERA units feature built-in reminders or smart alerts.',
            },
            {
                'category': 'installation',
                'sort_order': 4,
                'question': 'Is installation free, and how long does a technician visit take?',
                'answer': 'Standard demo installation is coordinated within 24 to 48 hours of booking. A qualified technician will inspect your water inlet pressure, mount the unit securely, verify water quality using a calibrated digital TDS meter, and guide you through daily use.',
            },
            {
                'category': 'general',
                'sort_order': 5,
                'question': 'Can I compare multiple purifiers before requesting a consultation?',
                'answer': 'Yes! You can use our built-in Compare tool (up to 3 models side-by-side) or the interactive Product Finder wizard to identify the best purifier matching your water source and family budget.',
            },
        ]

        for f in faqs_data:
            FAQ.objects.update_or_create(
                question=f['question'],
                defaults=f
            )
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(faqs_data)} FAQs seeded."))

        # 6. Default Admin and Demo Customer Accounts
        admin_user, admin_created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@aquavera.demo',
                'first_name': 'AQUAVERA',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+91 99999 11111',
                'city': 'New Delhi',
            }
        )
        if admin_created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Staff Admin user created: admin / Admin@12345"))
        else:
            self.stdout.write(self.style.NOTICE("* Staff Admin user already exists (admin)."))

        customer_user, cust_created = CustomUser.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@example.demo',
                'first_name': 'Sameer',
                'last_name': 'Kulkarni',
                'is_staff': False,
                'is_customer': True,
                'phone_number': '+91 98220 54321',
                'city': 'Pune',
                'address': 'Flat 402, Green Meadows, Baner Road, Pune 411045',
            }
        )
        if cust_created:
            customer_user.set_password('Customer@12345')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Demo Customer user created: customer / Customer@12345"))
        else:
            self.stdout.write(self.style.NOTICE("* Demo Customer user already exists (customer)."))

        # 7. Sample Initial Enquiry & Service Request for Dashboard
        first_product = Product.objects.filter(slug='aquavera-crystal-optima-ro').first()
        if not ProductEnquiry.objects.filter(customer_name='Sameer Kulkarni').exists():
            ProductEnquiry.objects.create(
                customer_name='Sameer Kulkarni',
                email='customer@example.demo',
                mobile='+91 98220 54321',
                city='Pune',
                user=customer_user,
                product=first_product,
                enquiry_type='consultation',
                message='Looking for home water purification for mixed borewell supply. Need TDS testing.',
                status='new',
                consent=True,
            )
            self.stdout.write(self.style.SUCCESS("[OK] Demo Product Enquiry created."))

        if not ServiceRequest.objects.filter(customer_name='Sameer Kulkarni').exists():
            ServiceRequest.objects.create(
                customer_name='Sameer Kulkarni',
                mobile='+91 98220 54321',
                email='customer@example.demo',
                city='Pune',
                user=customer_user,
                product_model='AQUAVERA Crystal Optima RO',
                service_type='installation',
                preferred_date=timezone.now().date() + datetime.timedelta(days=2),
                issue_description='Installation requested for newly delivered purifier in kitchen.',
                status='pending',
            )
            self.stdout.write(self.style.SUCCESS("[OK] Demo Service Request created."))

        self.stdout.write(self.style.SUCCESS("\n== AQUAVERA DEMO DATA SEEDED SUCCESSFULLY! =="))

