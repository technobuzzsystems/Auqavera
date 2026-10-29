from decimal import Decimal
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product, ProductImage

def create_test_image(filename="test.jpg"):
    file_obj = io.BytesIO()
    img = Image.new("RGB", (200, 200), color=(25, 182, 201))
    img.save(file_obj, format="JPEG")
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type="image/jpeg")

class CatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category_ro = Category.objects.create(
            name="RO Water Purifiers",
            slug="ro-water-purifiers",
            description="RO systems"
        )
        self.category_uv = Category.objects.create(
            name="UV Water Purifiers",
            slug="uv-water-purifiers",
            description="UV systems"
        )
        self.product_ro = Product.objects.create(
            name="AQUAVERA Test RO",
            slug="aquavera-test-ro",
            category=self.category_ro,
            short_description="Test RO",
            description="Complete description for test RO.",
            technology="RO + UV + UF",
            storage_capacity_liters=Decimal("8.5"),
            price=Decimal("15000.00"),
            original_price=Decimal("18000.00"),
            purification_stages="7 Stages",
            is_featured=True,
            is_active=True
        )
        self.product_uv = Product.objects.create(
            name="AQUAVERA Test UV",
            slug="aquavera-test-uv",
            category=self.category_uv,
            short_description="Test UV",
            description="Complete description for test UV.",
            technology="UV + UF",
            storage_capacity_liters=Decimal("6.0"),
            price=Decimal("8000.00"),
            purification_stages="4 Stages",
            is_featured=False,
            is_active=True
        )

    def test_product_list_status(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test RO")
        self.assertContains(response, "AQUAVERA Test UV")

    def test_category_filter(self):
        response = self.client.get(reverse('catalog:product_list') + '?category=ro-water-purifiers')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test RO")
        self.assertNotContains(response, "AQUAVERA Test UV")

    def test_search_filter(self):
        response = self.client.get(reverse('catalog:product_list') + '?q=Test+UV')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test UV")
        self.assertNotContains(response, "AQUAVERA Test RO")

    def test_sort_price_low(self):
        response = self.client.get(reverse('catalog:product_list') + '?sort=price_low')
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0], self.product_uv)
        self.assertEqual(products[1], self.product_ro)

    def test_product_detail_view(self):
        response = self.client.get(reverse('catalog:product_detail', kwargs={'slug': 'aquavera-test-ro'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test RO")
        self.assertContains(response, "7 Stages")
        # Check that CSS placeholder is rendered since image is None
        self.assertContains(response, "product-css-placeholder")

    def test_product_compare_view(self):
        response = self.client.get(reverse('catalog:product_compare') + f'?ids={self.product_ro.id},{self.product_uv.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test RO")
        self.assertContains(response, "AQUAVERA Test UV")

    def test_product_finder_view(self):
        response = self.client.get(reverse('catalog:product_finder') + '?find=1&source=borewell')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AQUAVERA Test RO")

    # Quick View / Preview Tests
    def test_product_preview_json_success(self):
        url = reverse('catalog:product_preview_json', kwargs={'pk': self.product_ro.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['id'], self.product_ro.id)
        self.assertEqual(data['name'], 'AQUAVERA Test RO')
        self.assertEqual(data['category'], 'RO Water Purifiers')
        self.assertEqual(data['technology'], 'RO + UV + UF')
        self.assertEqual(data['formatted_price'], '₹15,000')
        self.assertEqual(data['formatted_original_price'], '₹18,000')
        self.assertEqual(data['discount_percentage'], 17)
        self.assertEqual(data['storage_capacity_liters'], '8.5')
        self.assertEqual(data['purification_stages'], '7 Stages')
        self.assertIn('/products/aquavera-test-ro/', data['detail_url'])
        self.assertIn(f'/enquiry/?product={self.product_ro.id}', data['enquiry_url'])
        self.assertEqual(data['images'], [])

    def test_product_preview_json_with_gallery_images(self):
        img1 = ProductImage.objects.create(
            product=self.product_ro,
            image=create_test_image("ro_front.jpg"),
            alt_text="Front RO Angle",
            is_primary=True,
            display_order=0
        )
        img2 = ProductImage.objects.create(
            product=self.product_ro,
            image=create_test_image("ro_filter.jpg"),
            alt_text="Internal Membrane View",
            is_primary=False,
            display_order=1
        )

        url = reverse('catalog:product_preview_json', kwargs={'pk': self.product_ro.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data['images']), 2)
        self.assertEqual(data['images'][0]['alt'], 'Front RO Angle')
        self.assertTrue(data['images'][0]['is_primary'])
        self.assertEqual(data['images'][1]['alt'], 'Internal Membrane View')
        self.assertFalse(data['images'][1]['is_primary'])

    def test_product_preview_json_inactive_product_returns_404(self):
        draft_prod = Product.objects.create(
            name="AQUAVERA Hidden Draft",
            slug="aquavera-hidden-draft",
            category=self.category_ro,
            short_description="Draft",
            description="Draft",
            technology="RO",
            storage_capacity_liters=Decimal("7.0"),
            price=Decimal("12000.00"),
            purification_stages="5 Stages",
            status='draft',
            is_active=False
        )
        url = reverse('catalog:product_preview_json', kwargs={'pk': draft_prod.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_product_preview_json_invalid_id_returns_404(self):
        url = reverse('catalog:product_preview_json', kwargs={'pk': 999999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_product_card_renders_clickable_preview_trigger(self):
        # Homepage test
        home_res = self.client.get(reverse('pages:home'))
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, 'product-preview-trigger')
        self.assertContains(home_res, 'data-preview-url')
        self.assertContains(home_res, 'Quick View')
        self.assertContains(home_res, 'id="productPreviewModal"')

        # Catalog page test
        cat_res = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(cat_res.status_code, 200)
        self.assertContains(cat_res, 'product-preview-trigger')
        self.assertContains(cat_res, 'data-preview-url')
        self.assertContains(cat_res, 'Quick View')
        self.assertContains(cat_res, 'id="productPreviewModal"')

