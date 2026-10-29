from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.catalog.models import Category, Product
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest

class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = CustomUser.objects.create_user(
            username='staffadmin',
            email='staff@aquavera.demo',
            password='StaffPassword123!',
            is_staff=True
        )
        self.customer_user = CustomUser.objects.create_user(
            username='regcustomer',
            email='cust@aquavera.demo',
            password='CustPassword123!',
            is_staff=False
        )
        self.cat = Category.objects.create(name='RO', slug='ro')
        self.product = Product.objects.create(
            name='Dashboard Test Product',
            slug='dashboard-test-product',
            category=self.cat,
            short_description='Short',
            description='Desc',
            technology='RO',
            storage_capacity_liters=Decimal('8.0'),
            price=Decimal('10000.00'),
            purification_stages='5 Stages'
        )
        self.enquiry = ProductEnquiry.objects.create(
            customer_name='Enq Customer',
            email='enq@demo.com',
            mobile='9988776655',
            city='Noida',
            enquiry_type='general',
            message='Need assistance',
            status='new'
        )

    def test_anonymous_user_blocked_from_dashboard(self):
        # Anonymous users should be redirected to login
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse('accounts:login') in response.url)

    def test_normal_customer_blocked_from_dashboard(self):
        # Normal customers should be redirected to login with next parameter
        self.client.login(username='regcustomer', password='CustPassword123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_access_dashboard(self):
        self.client.login(username='staffadmin', password='StaffPassword123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Command Center')

    def test_staff_can_update_enquiry_status(self):
        self.client.login(username='staffadmin', password='StaffPassword123!')
        response = self.client.post(reverse('dashboard:enquiry_status', kwargs={'pk': self.enquiry.pk}), {
            'status': 'contacted'
        })
        self.assertRedirects(response, reverse('dashboard:enquiries'))
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, 'contacted')
