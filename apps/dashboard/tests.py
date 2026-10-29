import io
from decimal import Decimal
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import CustomUser
from apps.catalog.models import Category, Product, ProductImage, StockAdjustment
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest


def create_test_image(filename="test.jpg"):
    """Generate a valid in-memory JPEG image file for Pillow."""
    img = Image.new('RGB', (10, 10), color='teal')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile(filename, buf.getvalue(), content_type='image/jpeg')


class AdminPanelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(
            username='adminmaster',
            email='admin@aquavera.com',
            password='AdminPassword123!',
            is_staff=True,
            is_superuser=True
        )
        self.staff_user = CustomUser.objects.create_user(
            username='staffmanager',
            email='staff@aquavera.com',
            password='StaffPassword123!',
            is_staff=True,
            is_superuser=False
        )
        self.customer_user = CustomUser.objects.create_user(
            username='regularcustomer',
            email='cust@example.com',
            password='CustomerPassword123!',
            is_staff=False,
            is_customer=True
        )
        self.category = Category.objects.create(name='RO Water Purifiers', slug='ro-purifiers')
        self.product = Product.objects.create(
            name='AQUAVERA Test RO',
            slug='aquavera-test-ro',
            category=self.category,
            short_description='Short description for testing',
            description='Detailed specifications and description for testing',
            technology='RO + UV + TDS Control',
            storage_capacity_liters=Decimal('8.5'),
            price=Decimal('14990.00'),
            original_price=Decimal('17990.00'),
            purification_stages='7 Stages',
            stock_quantity=12,
            low_stock_threshold=4,
            status='published'
        )
        self.enquiry = ProductEnquiry.objects.create(
            customer_name='John Doe',
            email='john@example.com',
            mobile='9876543210',
            city='Bengaluru',
            enquiry_type='consultation',
            product=self.product,
            message='Inquiring about water TDS suitability.',
            status='new'
        )
        self.service_ticket = ServiceRequest.objects.create(
            customer_name='Sarah Connor',
            mobile='9123456780',
            email='sarah@example.com',
            city='Bengaluru',
            product_model='AQUAVERA Test RO',
            service_type='installation',
            preferred_date='2026-11-05',
            issue_description='Installation requested for new purifier.',
            status='pending'
        )

    # 1. Access Control
    def test_unauthenticated_user_redirected_to_admin_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_regular_customer_blocked_from_admin_panel(self):
        self.client.login(username='regularcustomer', password='CustomerPassword123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    # 2. Admin Authentication
    def test_staff_login_and_logout(self):
        # GET login page
        response = self.client.get(reverse('dashboard:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Username or Email')

        # POST login with valid credentials
        post_response = self.client.post(reverse('dashboard:login'), {
            'username': 'staffmanager',
            'password': 'StaffPassword123!',
        })
        self.assertRedirects(post_response, reverse('dashboard:home'))

        # POST logout
        logout_response = self.client.post(reverse('dashboard:logout'))
        self.assertRedirects(logout_response, reverse('dashboard:login'))

    # 3. Dashboard KPI Metrics
    def test_dashboard_home_renders_real_metrics(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Executive Command Center')
        self.assertEqual(response.context['total_products'], 1)
        self.assertEqual(response.context['published_products'], 1)
        self.assertEqual(response.context['total_enquiries'], 1)
        self.assertEqual(response.context['new_enquiries'], 1)
        self.assertEqual(response.context['total_inventory_units'], 12)

    # 4. Product CRUD & Public Website Synchronization
    def test_product_create_edit_and_public_sync(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # A. Create a new product
        create_data = {
            'name': 'AQUAVERA HydroPure Prime',
            'slug': 'aquavera-hydropure-prime',
            'sku': 'AQV-HP-001',
            'brand': 'AQUAVERA',
            'category': self.category.id,
            'short_description': 'New prime purifier for testing',
            'description': 'Full breakdown of filtration and features',
            'technology': 'RO + UV + Alkaline',
            'storage_capacity_liters': '9.0',
            'price': '18990.00',
            'original_price': '21990.00',
            'purification_stages': '8 Stages',
            'intended_use': 'Home / Office',
            'warranty_info': '1 Year Full Warranty',
            'maintenance_information': 'Bi-annual filter checkup',
            'stock_quantity': 10,
            'low_stock_threshold': 3,
            'status': 'published',
            'is_featured': True,
        }
        create_res = self.client.post(reverse('dashboard:product_create'), create_data)
        self.assertEqual(create_res.status_code, 302)

        new_prod = Product.objects.get(slug='aquavera-hydropure-prime')
        self.assertEqual(new_prod.name, 'AQUAVERA HydroPure Prime')
        self.assertTrue(new_prod.is_active)

        # B. Verify published product is visible in public catalogue
        pub_list = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(pub_list.status_code, 200)
        self.assertContains(pub_list, 'AQUAVERA HydroPure Prime')
        self.assertIn(new_prod, pub_list.context['products'])

        # C. Verify product detail page
        detail_res = self.client.get(reverse('catalog:product_detail', kwargs={'slug': new_prod.slug}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, 'AQUAVERA HydroPure Prime')
        self.assertContains(detail_res, '18,990')

        # D. Edit product price
        edit_data = create_data.copy()
        edit_data['price'] = '19490.00'
        edit_res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': new_prod.pk}), edit_data)
        self.assertEqual(edit_res.status_code, 302)

        new_prod.refresh_from_db()
        self.assertEqual(new_prod.price, Decimal('19490.00'))

        # E. Unpublish product (Draft) and verify hidden from public catalogue
        unpub_res = self.client.post(reverse('dashboard:product_toggle_status', kwargs={'pk': new_prod.pk}))
        self.assertEqual(unpub_res.status_code, 302)
        new_prod.refresh_from_db()
        self.assertEqual(new_prod.status, 'draft')
        self.assertFalse(new_prod.is_active)

        # Verify not in active products queryset
        pub_list_after = self.client.get(reverse('catalog:product_list'))
        self.assertNotIn(new_prod, pub_list_after.context['products'])

        # Verify customer without staff session cannot see draft product
        public_client = Client()
        public_res = public_client.get(reverse('catalog:product_list'))
        self.assertNotContains(public_res, 'AQUAVERA HydroPure Prime')

    # 5. Multiple Product Image Management
    def test_multiple_images_management(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Generate valid JPEG test images
        img1 = create_test_image("test_purifier1.jpg")
        img2 = create_test_image("test_purifier2.jpg")

        # Upload first image
        self.client.post(reverse('dashboard:product_images', kwargs={'pk': self.product.pk}), {
            'image': img1,
            'alt_text': 'Angle 1 Front',
            'is_primary': True,
            'display_order': 0,
        })
        self.assertEqual(self.product.images.count(), 1)
        self.assertEqual(self.product.primary_image.alt_text, 'Angle 1 Front')

        # Upload second image and set as primary
        self.client.post(reverse('dashboard:product_images', kwargs={'pk': self.product.pk}), {
            'image': img2,
            'alt_text': 'Angle 2 Side',
            'is_primary': True,
            'display_order': 1,
        })
        self.assertEqual(self.product.images.count(), 2)

        p_image = self.product.primary_image
        self.assertEqual(p_image.alt_text, 'Angle 2 Side')

        # Delete image
        del_res = self.client.post(reverse('dashboard:image_delete', kwargs={'image_id': p_image.id}))
        self.assertEqual(del_res.status_code, 302)
        self.assertEqual(self.product.images.count(), 1)

    # 6. Inventory & Stock Adjustment
    def test_stock_adjustment_and_audit_trail(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        initial_stock = self.product.stock_quantity  # 12

        # Positive stock adjustment (+5)
        adj_res = self.client.post(reverse('dashboard:inventory_adjust', kwargs={'product_id': self.product.id}), {
            'change_type': 'restock',
            'quantity_change': 5,
            'notes': 'Received batch #104 from manufacturing',
        })
        self.assertRedirects(adj_res, reverse('dashboard:inventory'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock + 5)

        # Audit log verification
        log_entry = StockAdjustment.objects.filter(product=self.product).latest('created_at')
        self.assertEqual(log_entry.quantity_change, 5)
        self.assertEqual(log_entry.previous_stock, initial_stock)
        self.assertEqual(log_entry.new_stock, initial_stock + 5)
        self.assertEqual(log_entry.created_by, self.staff_user)

        # Negative adjustment exceeding stock (should be rejected)
        fail_res = self.client.post(reverse('dashboard:inventory_adjust', kwargs={'product_id': self.product.id}), {
            'change_type': 'damaged',
            'quantity_change': -50,  # exceeds available 17
            'notes': 'Invalid excessive reduction',
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 17)  # Remains unchanged

    # 7. Customer Enquiry Management
    def test_customer_enquiry_review_and_status_update(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Quick status update
        self.client.post(reverse('dashboard:enquiry_status', kwargs={'pk': self.enquiry.pk}), {
            'status': 'in_progress'
        })
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, 'in_progress')

        # Full detail update with notes
        detail_res = self.client.post(reverse('dashboard:enquiry_detail', kwargs={'pk': self.enquiry.pk}), {
            'status': 'converted',
            'assigned_to': self.staff_user.id,
            'follow_up_date': '2026-11-10',
            'internal_notes': 'Customer raw TDS is 650 ppm. Recommended Crystal Optima RO.',
        })
        self.assertRedirects(detail_res, reverse('dashboard:enquiry_detail', kwargs={'pk': self.enquiry.pk}))
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, 'converted')
        self.assertEqual(self.enquiry.assigned_to, self.staff_user)
        self.assertIn('Customer raw TDS is 650 ppm', self.enquiry.internal_notes)

    # 8. Category Management
    def test_category_create_and_safe_deletion(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Create category
        cat_res = self.client.post(reverse('dashboard:category_create'), {
            'name': 'UV Water Purifiers',
            'slug': 'uv-purifiers',
            'description': 'Disinfection category',
            'icon': 'bi-sun',
            'sort_order': 2,
            'is_active': True,
        })
        self.assertRedirects(cat_res, reverse('dashboard:categories'))
        self.assertTrue(Category.objects.filter(slug='uv-purifiers').exists())

        # Safe deactivation of category with products
        del_res = self.client.post(reverse('dashboard:category_delete', kwargs={'pk': self.category.pk}))
        self.assertRedirects(del_res, reverse('dashboard:categories'))
        self.category.refresh_from_db()
        # Because self.category has self.product attached, it should be deactivated rather than deleted
        self.assertFalse(self.category.is_active)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    # 9. Toggle Featured on Homepage
    def test_product_toggle_featured(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        self.product.is_featured = True
        self.product.save()

        # Toggle OFF
        res = self.client.post(reverse('dashboard:product_toggle_featured', kwargs={'pk': self.product.pk}))
        self.assertEqual(res.status_code, 302)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_featured)

        # Toggle ON
        res2 = self.client.post(reverse('dashboard:product_toggle_featured', kwargs={'pk': self.product.pk}))
        self.assertEqual(res2.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_featured)

    # 10. Multiple Product Images in Create & Edit
    def test_product_create_with_multiple_images_and_primary_selection(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        img1 = create_test_image('front_view.jpg')
        img2 = create_test_image('side_view.jpg')
        img3 = create_test_image('filter_view.jpg')

        post_data = {
            'name': 'AQUAVERA Crystal Multi-Stage',
            'brand': 'AQUAVERA',
            'category': self.category.pk,
            'short_description': 'Advanced 8-stage purifier',
            'description': 'Complete multi-barrier pure water tech',
            'technology': 'RO + UV + Copper',
            'storage_capacity_liters': '10.0',
            'price': '18500',
            'original_price': '22000',
            'purification_stages': '8 Stages',
            'intended_use': 'Residential / Villa',
            'stock_quantity': '10',
            'low_stock_threshold': '3',
            'status': 'published',
            'is_featured': True,
            'new_images': [img1, img2, img3],
            'primary_image_choice': 'new_1',
            'new_image_alt_0': 'Front View Shot',
            'new_image_alt_1': 'Side Angle Primary Shot',
            'new_image_alt_2': 'Filter Cartridge Internal',
        }

        res = self.client.post(reverse('dashboard:product_create'), post_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        new_prod = Product.objects.get(name='AQUAVERA Crystal Multi-Stage')
        self.assertEqual(new_prod.images.count(), 3)

        prim = new_prod.primary_image
        self.assertIsNotNone(prim)
        self.assertEqual(prim.alt_text, 'Side Angle Primary Shot')
        self.assertEqual(new_prod.display_image_url, prim.image.url)
        self.assertEqual(new_prod.image, prim.image)

        # Check thumbnail renders in admin products table
        admin_list_res = self.client.get(reverse('dashboard:products'))
        self.assertContains(admin_list_res, prim.image.url)
        self.assertContains(admin_list_res, 'width: 56px; height: 56px')

        # Check public detail page shows primary and gallery
        pub_client = Client()
        pub_detail_res = pub_client.get(reverse('catalog:product_detail', kwargs={'slug': new_prod.slug}))
        self.assertEqual(pub_detail_res.status_code, 200)
        self.assertContains(pub_detail_res, prim.image.url)

    def test_product_edit_image_management_delete_and_reprimary(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Set up product with 2 initial images
        img1 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image('img1.jpg'),
            alt_text='Initial First',
            is_primary=True,
            display_order=0
        )
        img2 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image('img2.jpg'),
            alt_text='Initial Second',
            is_primary=False,
            display_order=1
        )
        self.product.image = img1.image
        self.product.save()

        # Edit: delete img1, upload img3, set img2 as primary, update img2 alt text
        img3 = create_test_image('img3.jpg')
        edit_data = {
            'name': self.product.name,
            'brand': self.product.brand,
            'category': self.product.category_id,
            'short_description': self.product.short_description,
            'description': self.product.description,
            'technology': self.product.technology,
            'storage_capacity_liters': self.product.storage_capacity_liters,
            'price': self.product.price,
            'original_price': self.product.original_price,
            'purification_stages': self.product.purification_stages,
            'intended_use': self.product.intended_use,
            'stock_quantity': self.product.stock_quantity,
            'low_stock_threshold': self.product.low_stock_threshold,
            'status': self.product.status,
            'delete_image_ids': [img1.id],
            f'existing_alt_{img2.id}': 'Updated Second Alt Text',
            'primary_image_choice': f'existing_{img2.id}',
            'new_images': [img3],
            'new_image_alt_0': 'Newly Added Image 3',
        }

        res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), edit_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        self.product.refresh_from_db()
        # img1 should be deleted, so count should be 2 (img2 + img3)
        self.assertEqual(self.product.images.count(), 2)
        self.assertFalse(ProductImage.objects.filter(id=img1.id).exists())

        img2.refresh_from_db()
        self.assertTrue(img2.is_primary)
        self.assertEqual(img2.alt_text, 'Updated Second Alt Text')
        self.assertEqual(self.product.image, img2.image)

    def test_image_validation_rejects_invalid_file_format(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        bad_file = SimpleUploadedFile("script.py", b"print('malicious')", content_type="text/plain")

        post_data = {
            'name': 'AQUAVERA Malicious File Test',
            'category': self.category.pk,
            'short_description': 'Test invalid file',
            'description': 'Testing rejection of non-image files',
            'technology': 'RO',
            'storage_capacity_liters': '8',
            'price': '10000',
            'purification_stages': '5 Stages',
            'intended_use': 'Home',
            'status': 'published',
            'new_images': [bad_file],
        }

        res = self.client.post(reverse('dashboard:product_create'), post_data)
        self.assertEqual(res.status_code, 200) # Form re-rendered with error
        self.assertFalse(Product.objects.filter(name='AQUAVERA Malicious File Test').exists())

    # 9. Multiple Images Direct Upload in Product Creation Form
    def test_product_creation_with_multiple_images_and_primary_selection(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Generate 3 valid JPEG images
        img1 = create_test_image("angle_front.jpg")
        img2 = create_test_image("angle_side.jpg")
        img3 = create_test_image("angle_filters.jpg")

        post_data = {
            'name': 'AQUAVERA MultiPhoto Elite',
            'slug': 'aquavera-multiphoto-elite',
            'sku': 'AQV-MPE-901',
            'brand': 'AQUAVERA',
            'category': self.category.id,
            'short_description': 'Purifier tested with multiple uploaded images',
            'description': 'Full detailed specs for testing multiple image uploads',
            'technology': 'RO + UV + Mineralizer',
            'storage_capacity_liters': '10.0',
            'price': '19990.00',
            'original_price': '22990.00',
            'purification_stages': '8 Stages',
            'intended_use': 'Home / Villa',
            'warranty_info': '1 Year Full Coverage',
            'stock_quantity': 25,
            'low_stock_threshold': 5,
            'status': 'published',
            'is_featured': True,
            # 3 images uploaded simultaneously
            'new_images': [img1, img2, img3],
            'primary_image_choice': 'new_1',  # Mark 2nd image (index 1) as primary
            'new_image_alt_0': 'Angle 1 - Front Facing View',
            'new_image_alt_1': 'Angle 2 - Side Profile with Minerals',
            'new_image_alt_2': 'Angle 3 - Inside Purification Tank',
        }

        res = self.client.post(reverse('dashboard:product_create'), post_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        prod = Product.objects.get(slug='aquavera-multiphoto-elite')
        self.assertEqual(prod.images.count(), 3)

        # Verify image at index 1 is designated as primary
        primary = prod.primary_image
        self.assertIsNotNone(primary)
        self.assertTrue(primary.is_primary)
        self.assertEqual(primary.alt_text, 'Angle 2 - Side Profile with Minerals')

        # Verify display_image_url points to the primary image
        self.assertEqual(prod.display_image_url, primary.image.url)

        # Verify product management list table contains thumbnail
        table_res = self.client.get(reverse('dashboard:products'))
        self.assertEqual(table_res.status_code, 200)
        self.assertContains(table_res, primary.image.url)

        # Verify public product list contains thumbnail
        pub_client = Client()
        pub_list_res = pub_client.get(reverse('catalog:product_list'))
        self.assertEqual(pub_list_res.status_code, 200)
        self.assertContains(pub_list_res, primary.image.url)

        # Verify public detail page contains primary image and all 3 gallery images
        detail_res = pub_client.get(reverse('catalog:product_detail', kwargs={'slug': prod.slug}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, primary.image.url)
        for g_img in prod.images.all():
            self.assertContains(detail_res, g_img.image.url)

    # 10. Edit Product: Add image, switch primary, and delete image
    def test_product_edit_image_management(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # Set up 2 initial images for product
        img_a = ProductImage.objects.create(
            product=self.product,
            image=create_test_image("initial_a.jpg"),
            alt_text="Initial Photo A",
            is_primary=True,
            display_order=0
        )
        img_b = ProductImage.objects.create(
            product=self.product,
            image=create_test_image("initial_b.jpg"),
            alt_text="Initial Photo B",
            is_primary=False,
            display_order=1
        )
        self.assertEqual(self.product.images.count(), 2)

        # Edit form submission: upload img_c, set img_c as primary, delete img_a
        img_c = create_test_image("new_c.jpg")
        edit_data = {
            'name': self.product.name,
            'slug': self.product.slug,
            'sku': self.product.sku,
            'brand': self.product.brand,
            'category': self.category.id,
            'short_description': self.product.short_description,
            'description': self.product.description,
            'technology': self.product.technology,
            'storage_capacity_liters': str(self.product.storage_capacity_liters),
            'price': str(self.product.price),
            'original_price': str(self.product.original_price),
            'purification_stages': self.product.purification_stages,
            'intended_use': self.product.intended_use,
            'warranty_info': self.product.warranty_info,
            'stock_quantity': self.product.stock_quantity,
            'low_stock_threshold': self.product.low_stock_threshold,
            'status': self.product.status,
            'new_images': [img_c],
            'primary_image_choice': 'new_0',  # Newly uploaded image as primary
            'new_image_alt_0': 'New Photo C Front View',
            'delete_image_ids': [img_a.id],  # Delete Photo A
            f'existing_alt_{img_b.id}': 'Updated Photo B Alt',
        }

        edit_res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), edit_data)
        self.assertRedirects(edit_res, reverse('dashboard:products'))

        self.product.refresh_from_db()
        self.assertEqual(self.product.images.count(), 2)  # img_a deleted, img_c added, img_b preserved
        self.assertFalse(self.product.images.filter(id=img_a.id).exists())

        # Check new primary
        new_primary = self.product.primary_image
        self.assertEqual(new_primary.alt_text, 'New Photo C Front View')
        self.assertTrue(new_primary.is_primary)

        # Check updated existing alt
        img_b.refresh_from_db()
        self.assertEqual(img_b.alt_text, 'Updated Photo B Alt')
        self.assertFalse(img_b.is_primary)

    # 11. Image Upload Validation Errors
    def test_image_validation_rejections(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        # A. Unsupported extension (.txt)
        bad_file = SimpleUploadedFile("malicious.txt", b"plain text content", content_type="text/plain")
        res_bad = self.client.post(reverse('dashboard:product_create'), {
            'name': 'Bad File Product',
            'slug': 'bad-file-product',
            'category': self.category.id,
            'short_description': 'Short',
            'description': 'Desc',
            'technology': 'RO',
            'storage_capacity_liters': '8.0',
            'price': '10000.00',
            'purification_stages': '5 Stages',
            'new_images': [bad_file],
        })
        self.assertEqual(res_bad.status_code, 200)
        self.assertFalse(Product.objects.filter(slug='bad-file-product').exists())

        # B. Oversized file (> 5MB)
        oversized_bytes = b"0" * (5 * 1024 * 1024 + 1024)  # 5MB + 1KB
        oversized_file = SimpleUploadedFile("huge.jpg", oversized_bytes, content_type="image/jpeg")
        res_oversized = self.client.post(reverse('dashboard:product_create'), {
            'name': 'Oversized Product',
            'slug': 'oversized-product',
            'category': self.category.id,
            'short_description': 'Short',
            'description': 'Desc',
            'technology': 'RO',
            'storage_capacity_liters': '8.0',
            'price': '10000.00',
            'purification_stages': '5 Stages',
            'new_images': [oversized_file],
        })
        self.assertEqual(res_oversized.status_code, 200)
        self.assertFalse(Product.objects.filter(slug='oversized-product').exists())

    # 12. Product without image uses placeholder cleanly
    def test_product_without_image_placeholder(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')

        prod_no_img = Product.objects.create(
            name='AQUAVERA No Image Model',
            slug='aquavera-no-image-model',
            category=self.category,
            short_description='Testing placeholder fallback',
            description='Detailed specs for placeholder testing',
            technology='UV + UF',
            storage_capacity_liters=Decimal('7.0'),
            price=Decimal('8990.00'),
            purification_stages='6 Stages',
            status='published'
        )

        # display_image_url should be None
        self.assertIsNone(prod_no_img.display_image_url)

        # Admin table shows placeholder
        admin_res = self.client.get(reverse('dashboard:products'))
        self.assertContains(admin_res, 'bi-water')

        # Public card shows CSS placeholder
        pub_client = Client()
        pub_res = pub_client.get(reverse('catalog:product_list'))
        self.assertContains(pub_res, 'product-css-placeholder')

    # 13. Regression: Edit product without changing images
    def test_edit_product_without_changing_images(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        img = ProductImage.objects.create(
            product=self.product,
            image=create_test_image('keep.jpg'),
            alt_text='Keep This Image',
            is_primary=True,
            display_order=0
        )
        self.product.image = img.image
        self.product.save()

        edit_data = {
            'name': 'AQUAVERA Crystal Optima RO Updated',
            'brand': self.product.brand,
            'category': self.product.category_id,
            'short_description': 'Updated description',
            'description': self.product.description,
            'technology': self.product.technology,
            'storage_capacity_liters': self.product.storage_capacity_liters,
            'price': '16999.00',
            'original_price': '19999.00',
            'purification_stages': self.product.purification_stages,
            'intended_use': self.product.intended_use,
            'stock_quantity': '18',
            'low_stock_threshold': '5',
            'status': 'published',
            'is_featured': True,
        }
        res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), edit_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'AQUAVERA Crystal Optima RO Updated')
        self.assertEqual(self.product.price, Decimal('16999.00'))
        self.assertEqual(self.product.stock_quantity, 18)
        self.assertTrue(self.product.is_featured)
        self.assertEqual(self.product.images.count(), 1)
        self.assertEqual(self.product.image, img.image)

    # 14. Regression: Edit product with browser-simulated image removal (deleting image with existing_alt submitted)
    def test_edit_product_remove_image_with_browser_alt_inputs(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        img1 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image('remove_me.jpg'),
            alt_text='Delete Me',
            is_primary=True,
            display_order=0
        )
        img2 = ProductImage.objects.create(
            product=self.product,
            image=create_test_image('remain.jpg'),
            alt_text='Stay Primary',
            is_primary=False,
            display_order=1
        )
        self.product.image = img1.image
        self.product.save()

        # Real browsers submit all inputs in the form, including existing_alt for images marked for deletion
        edit_data = {
            'name': self.product.name,
            'brand': self.product.brand,
            'category': self.product.category_id,
            'short_description': self.product.short_description,
            'description': self.product.description,
            'technology': self.product.technology,
            'storage_capacity_liters': self.product.storage_capacity_liters,
            'price': self.product.price,
            'original_price': self.product.original_price or '',
            'purification_stages': self.product.purification_stages,
            'intended_use': self.product.intended_use,
            'stock_quantity': self.product.stock_quantity,
            'low_stock_threshold': self.product.low_stock_threshold,
            'status': self.product.status,
            'delete_image_ids': [img1.id],
            f'existing_alt_{img1.id}': 'Delete Me Alt',
            f'existing_alt_{img2.id}': 'Stay Primary Updated',
            'primary_image_choice': f'existing_{img2.id}',
        }
        res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), edit_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        self.product.refresh_from_db()
        self.assertEqual(self.product.images.count(), 1)
        self.assertFalse(ProductImage.objects.filter(id=img1.id).exists())

        img2.refresh_from_db()
        self.assertTrue(img2.is_primary)
        self.assertEqual(img2.alt_text, 'Stay Primary Updated')
        self.assertEqual(self.product.image, img2.image)

    # 15. Regression: Nonexistent product edit returns 404
    def test_edit_nonexistent_product_returns_404(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        res_get = self.client.get(reverse('dashboard:product_edit', kwargs={'pk': 999999}))
        self.assertEqual(res_get.status_code, 404)
        res_post = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': 999999}), {'name': 'Fake'})
        self.assertEqual(res_post.status_code, 404)

    # 16. Regression: Failed validation does not corrupt existing product data
    def test_failed_validation_preserves_product_data(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        orig_price = self.product.price
        orig_name = self.product.name

        # Invalid selling price greater than original price (original_price < price is rejected by clean())
        bad_data = {
            'name': 'Corrupted Name Attempt',
            'brand': self.product.brand,
            'category': self.product.category_id,
            'short_description': self.product.short_description,
            'description': self.product.description,
            'technology': self.product.technology,
            'storage_capacity_liters': self.product.storage_capacity_liters,
            'price': '30000.00',
            'original_price': '20000.00',
            'purification_stages': self.product.purification_stages,
            'intended_use': self.product.intended_use,
            'stock_quantity': self.product.stock_quantity,
            'low_stock_threshold': self.product.low_stock_threshold,
            'status': self.product.status,
        }
        res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), bad_data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Original M.R.P. cannot be lower than the selling price.")

        self.product.refresh_from_db()
        self.assertEqual(self.product.name, orig_name)
        self.assertEqual(self.product.price, orig_price)

    # 17. Regression: Public website synchronization after product edit
    def test_public_website_synchronization_after_edit(self):
        self.client.login(username='staffmanager', password='StaffPassword123!')
        edit_data = {
            'name': 'AQUAVERA Crystal Optima Sync Test',
            'brand': self.product.brand,
            'category': self.product.category_id,
            'short_description': 'Synchronized public description',
            'description': 'Full description after edit',
            'technology': 'RO + UV + Copper Tech',
            'storage_capacity_liters': '10.5',
            'price': '17450.00',
            'original_price': '21000.00',
            'purification_stages': '8 Stages',
            'intended_use': 'Commercial / Home',
            'stock_quantity': '7',
            'low_stock_threshold': '2',
            'status': 'published',
            'is_featured': True,
        }
        res = self.client.post(reverse('dashboard:product_edit', kwargs={'pk': self.product.pk}), edit_data)
        self.assertRedirects(res, reverse('dashboard:products'))

        # Public user checks catalog and detail
        pub_client = Client()
        pub_cat = pub_client.get(reverse('catalog:product_list'))
        self.assertEqual(pub_cat.status_code, 200)
        self.assertContains(pub_cat, 'AQUAVERA Crystal Optima Sync Test')
        self.assertContains(pub_cat, '17,450')

        self.product.refresh_from_db()
        pub_detail = pub_client.get(reverse('catalog:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(pub_detail.status_code, 200)
        self.assertContains(pub_detail, 'AQUAVERA Crystal Optima Sync Test')
        self.assertContains(pub_detail, 'RO + UV + Copper Tech')
