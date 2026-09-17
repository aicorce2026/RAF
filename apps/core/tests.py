from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class CoreInterfaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_home_page_returns_200(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_page_contains_arabic_content(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, 'المكتبة الرقمية')

    def test_rtl_document_direction(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, 'lang="ar"')
        self.assertContains(response, 'dir="rtl"')

    def test_shared_base_navigation(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, '<nav')
        self.assertContains(response, 'الرئيسية')
        self.assertContains(response, 'الكتب')

    def test_anonymous_navigation(self):
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('accounts:login'))
        self.assertContains(response, reverse('accounts:register'))
        self.assertNotContains(response, 'تسجيل الخروج')

    def test_authenticated_navigation(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.home_url)
        self.assertContains(response, reverse('accounts:profile'))
        self.assertContains(response, 'تسجيل الخروج')
        self.assertNotContains(response, reverse('accounts:login'))

    def test_logout_is_post(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.home_url)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, reverse('accounts:logout'))
        # Ensure it's not just a regular href link
        self.assertNotContains(response, f'href="{reverse("accounts:logout")}"')
