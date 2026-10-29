from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product

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
