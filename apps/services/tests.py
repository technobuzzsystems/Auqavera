from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from apps.services.models import ServiceRequest

class ServiceRequestTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_service_request_submission(self):
        future_date = date.today() + timedelta(days=3)
        response = self.client.post(reverse('services:service_request_form'), {
            'customer_name': 'Anita Roy',
            'mobile': '9811122233',
            'email': 'anita@example.com',
            'city': 'Delhi',
            'product_model': 'AQUAVERA Crystal Optima RO',
            'service_type': 'maintenance',
            'preferred_date': future_date.strftime('%Y-%m-%d'),
            'issue_description': 'Annual filter change and TDS check requested.',
            'honeypot': ''
        })
        self.assertRedirects(response, reverse('services:service_request_success'))
        srv = ServiceRequest.objects.filter(customer_name='Anita Roy').first()
        self.assertIsNotNone(srv)
        self.assertTrue(srv.reference_number.startswith('SRV-'))
        self.assertEqual(srv.status, 'pending')

    def test_past_date_rejected(self):
        past_date = date.today() - timedelta(days=2)
        response = self.client.post(reverse('services:service_request_form'), {
            'customer_name': 'Anita Roy',
            'mobile': '9811122233',
            'city': 'Delhi',
            'product_model': 'AQUAVERA Crystal Optima RO',
            'service_type': 'repair',
            'preferred_date': past_date.strftime('%Y-%m-%d'),
            'issue_description': 'Leakage repair',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ServiceRequest.objects.filter(customer_name='Anita Roy').exists())
