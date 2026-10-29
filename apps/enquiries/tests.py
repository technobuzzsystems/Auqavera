from django.test import TestCase, Client
from django.urls import reverse
from apps.enquiries.models import ProductEnquiry
from apps.catalog.models import Category, Product
from decimal import Decimal

class EnquiryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="RO", slug="ro")
        self.product = Product.objects.create(
            name="Optima RO",
            slug="optima-ro",
            category=self.category,
            short_description="Optima",
            description="Full",
            technology="RO",
            storage_capacity_liters=Decimal("8.0"),
            price=Decimal("12000.00"),
            purification_stages="6 Stages"
        )

    def test_valid_enquiry_submission(self):
        response = self.client.post(reverse('enquiries:submit_enquiry'), {
            'customer_name': 'Rahul Sharma',
            'email': 'rahul@example.com',
            'mobile': '9876543210',
            'city': 'Mumbai',
            'product': self.product.id,
            'enquiry_type': 'consultation',
            'message': 'Need advice on borewell filtration and installation.',
            'consent': True,
            'honeypot': ''
        })
        self.assertRedirects(response, reverse('enquiries:enquiry_success'))
        enquiry = ProductEnquiry.objects.filter(email='rahul@example.com').first()
        self.assertIsNotNone(enquiry)
        self.assertTrue(enquiry.reference_number.startswith('ENQ-'))
        self.assertEqual(enquiry.status, 'new')

    def test_invalid_enquiry_mobile(self):
        # Invalid mobile number with letters
        response = self.client.post(reverse('enquiries:submit_enquiry'), {
            'customer_name': 'Rahul Sharma',
            'email': 'rahul@example.com',
            'mobile': 'invalid123',
            'city': 'Mumbai',
            'enquiry_type': 'general',
            'message': 'Message text',
            'consent': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ProductEnquiry.objects.filter(email='rahul@example.com').exists())

    def test_honeypot_spam_rejection(self):
        # Bot filled honeypot
        response = self.client.post(reverse('enquiries:submit_enquiry'), {
            'customer_name': 'Bot Spammer',
            'email': 'bot@spam.com',
            'mobile': '9876543210',
            'city': 'SpamCity',
            'enquiry_type': 'general',
            'message': 'Spam content',
            'consent': True,
            'honeypot': 'I am a bot'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ProductEnquiry.objects.filter(email='bot@spam.com').exists())
