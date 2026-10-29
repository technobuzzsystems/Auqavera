from django.test import TestCase, Client
from django.urls import reverse
from apps.content.models import NewsletterSubscriber, SiteSetting

class ContentPagesTests(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSetting.load()

    def test_homepage_loads(self):
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AQUAVERA')
        self.assertContains(response, 'A NEW STANDARD OF PURITY')
        self.assertContains(response, 'Better Water.')
        self.assertContains(response, 'Better Everyday.')


    def test_about_page_loads(self):
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Mission')

    def test_contact_page_loads_and_submits(self):
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)

        post_resp = self.client.post(reverse('pages:contact'), {
            'full_name': 'Meera Sen',
            'email': 'meera@example.com',
            'phone': '9876543210',
            'subject': 'Water test query',
            'message': 'Do you test TDS at home?'
        })
        self.assertRedirects(post_resp, reverse('pages:contact'))

    def test_newsletter_subscription(self):
        response = self.client.post(reverse('pages:newsletter_subscribe'), {
            'email': 'subscriber@example.com',
            'honeypot': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='subscriber@example.com').exists())

    def test_robots_txt(self):
        response = self.client.get(reverse('pages:robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'User-agent: *')

    def test_sitemap_xml(self):
        response = self.client.get(reverse('pages:sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response, '<urlset')
