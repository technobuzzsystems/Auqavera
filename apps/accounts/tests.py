from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.enquiries.models import ProductEnquiry
from apps.services.models import ServiceRequest
from datetime import date, timedelta

class AccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Password123!',
            first_name='User',
            last_name='One'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Password123!',
            first_name='User',
            last_name='Two'
        )
        # Create enquiry for user1
        self.enq1 = ProductEnquiry.objects.create(
            customer_name='User One',
            email='user1@example.com',
            mobile='9800011111',
            city='Pune',
            user=self.user1,
            enquiry_type='consultation',
            message='User 1 private enquiry',
            status='new'
        )
        # Create enquiry for user2
        self.enq2 = ProductEnquiry.objects.create(
            customer_name='User Two',
            email='user2@example.com',
            mobile='9800022222',
            city='Mumbai',
            user=self.user2,
            enquiry_type='quote',
            message='User 2 private enquiry',
            status='new'
        )

    def test_customer_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcustomer',
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'phone_number': '9876500000',
            'city': 'Bengaluru',
            'password1': 'Secret@12345',
            'password2': 'Secret@12345',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertTrue(CustomUser.objects.filter(username='newcustomer').exists())

    def test_customer_login_and_logout(self):
        login_success = self.client.login(username='user1', password='Password123!')
        self.assertTrue(login_success)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

        # Logout
        logout_resp = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(logout_resp, reverse('pages:home'))

    def test_customer_privacy_isolation(self):
        # User 1 should see only their own enquiry, not User 2's
        self.client.login(username='user1', password='Password123!')
        response = self.client.get(reverse('accounts:my_enquiries'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User 1 private enquiry')
        self.assertNotContains(response, 'User 2 private enquiry')
