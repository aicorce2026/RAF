from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')

        # We also need a user for login tests
        self.user = User.objects.create_user(username='existinguser', password='existingpassword123')

    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_valid_registration_creates_user(self):
        data = {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Test password hashing
        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('newpassword123'))
        self.assertNotEqual(user.password, 'newpassword123')

    def test_invalid_registration(self):
        data = {
            'username': 'baduser',
            'password1': 'password123',
            'password2': 'different'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_duplicate_username_is_rejected(self):
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'password1': 'anotherpassword123',
            'password2': 'anotherpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_password_validators_reject_numeric_password(self):
        response = self.client.post(self.register_url, {
            'username': 'numericpassworduser',
            'password1': '12345678',
            'password2': '12345678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='numericpassworduser').exists())

    def test_registration_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(self.register_url, {
            'username': 'csrfuser',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username='csrfuser').exists())

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        data = {
            'username': 'existinguser',
            'password': 'existingpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)

        # Check authentication using session
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_accepts_local_next_url(self):
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'existingpassword123',
            'next': '/books/',
        })
        self.assertRedirects(response, '/books/')

    def test_login_rejects_external_next_url(self):
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'existingpassword123',
            'next': 'https://example.com/steal-session',
        })
        self.assertRedirects(response, self.profile_url)

    def test_login_rejects_protocol_relative_next_url(self):
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'existingpassword123',
            'next': '//example.com/steal-session',
        })
        self.assertRedirects(response, self.profile_url)

    def test_invalid_login(self):
        data = {
            'username': 'existinguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_anonymous_user_cannot_access_profile(self):
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')

    def test_authenticated_user_can_access_profile(self):
        self.client.login(username='existinguser', password='existingpassword123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existinguser')

    def test_logout(self):
        self.client.login(username='existinguser', password='existingpassword123')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_get_is_rejected_without_changing_session(self):
        self.client.login(username='existinguser', password='existingpassword123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        response = csrf_client.post(self.logout_url)
        self.assertEqual(response.status_code, 403)
        self.assertIn('_auth_user_id', csrf_client.session)

    def test_authenticated_user_redirected_from_register(self):
        self.client.login(username='existinguser', password='existingpassword123')
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)
