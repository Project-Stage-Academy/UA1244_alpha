from django.contrib.auth.password_validation import validate_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from forum import settings
from .models import User, Role

PASSWORD_VALIDATORS = []


class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name='Admin')
        self.user_role = Role.objects.create(name='User')
        self.investor_role = Role.objects.create(name='Investor')
        self.startup_role = Role.objects.create(name='Startup')

        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_user.roles.add(self.admin_role)

        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword',
            first_name='John',
            last_name='Doe',
            user_phone='+11234567890'
        )
        self.regular_user.roles.add(self.user_role)

    def login_user(self, email, password):
        response = self.client.post(
            reverse('token-create'),
            data={'email': email, 'password': password},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def add_role(self, token, role_name, user_id=None):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'role_name': role_name}
        if user_id:
            data['user_id'] = user_id
        return self.client.post(reverse('add-role'), data=data, format='json')

    def remove_role(self, token, role_name):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return self.client.post(reverse('remove-role'), data={'role_name': role_name}, format='json')

    def set_active_role(self, token, role_name):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return self.client.post(reverse('set-active-role'), data={'role_name': role_name}, format='json')

    def test_user_login(self):
        """Test user login"""
        token = self.login_user('user@example.com', 'userpassword')
        self.assertIsNotNone(token)

    def test_user_profile_retrieval(self):
        """Test retrieval of user profile"""
        token = self.login_user('user@example.com', 'userpassword')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_response = self.client.get(reverse('user-profile'))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], 'user@example.com')

    def test_regular_user_cannot_add_admin_role(self):
        """Test that regular user cannot add Admin role"""
        user_token = self.login_user('user@example.com', 'userpassword')
        response = self.add_role(user_token, 'Admin')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_add_allowed_roles(self):
        """Test that regular user can add allowed roles"""
        user_token = self.login_user('user@example.com', 'userpassword')

        response = self.add_role(user_token, 'Investor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.add_role(user_token, 'Startup')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_add_admin_role(self):
        """Test that admin can add Admin role to other users"""
        admin_token = self.login_user('admin@example.com', 'adminpassword')
        response = self.add_role(admin_token, 'Admin', self.regular_user.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_see_all_assigned_roles(self):
        user_token = self.login_user('user@example.com', 'userpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

        self.add_role(user_token, 'Investor')
        self.add_role(user_token, 'Startup')

        response = self.client.get(reverse('get-roles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('User', response.data['roles'])
        self.assertIn('Investor', response.data['roles'])
        self.assertIn('Startup', response.data['roles'])

    def test_user_can_remove_roles(self):
        user_token = self.login_user('user@example.com', 'userpassword')

        self.add_role(user_token, 'Investor')

        response = self.remove_role(user_token, 'Investor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = self.client.get(reverse('get-roles'))
        self.assertNotIn('Investor', response.data['roles'])

    def test_user_can_set_active_role(self):
        user_token = self.login_user('user@example.com', 'userpassword')

        self.add_role(user_token, 'Investor')

        response = self.set_active_role(user_token, 'Investor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = self.client.get(reverse('get-active-role'))
        self.assertEqual(response.data['active_role'], 'Investor')

    def test_remove_non_existent_role(self):
        user_token = self.login_user('user@example.com', 'userpassword')
        response = self.remove_role(user_token, 'NonExistentRole')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_non_existent_active_role(self):
        user_token = self.login_user('user@example.com', 'userpassword')
        response = self.set_active_role(user_token, 'NonExistentRole')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_active_role(self):
        user_token = self.login_user('user@example.com', 'userpassword')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')

        response = self.client.get(reverse('get-active-role'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_role', response.data)
        self.assertIn('all_roles', response.data)


class CustomTokenObtainPairViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('token-create')
        self.valid_password = 'StrongPass123!'
        self.test_password = 'StrongPass123!'
        self.active_user = User.objects.create_user(
            email='active@test.com',
            password=self.valid_password,
            is_active=True,
            is_soft_deleted=False
        )
        self.soft_deleted_user = User.objects.create_user(
            email='soft_deleted@test.com',
            password=self.valid_password,
            is_active=True,
            is_soft_deleted=True
        )
        self.inactive_user = User.objects.create_user(
            email='inactive@test.com',
            password=self.valid_password,
            is_active=False,
            is_soft_deleted=False
        )

    def test_active_user_can_obtain_token(self):
        response = self.client.post(
            self.url,
            {
                'email': 'active@test.com',
                'password': self.valid_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_password_format(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@test.com',
                password='short'
            )

    def test_active_user_can_obtain_token(self):
        response = self.client.post(
            self.url,
            {
                'email': 'active@test.com',
                'password': self.valid_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_soft_deleted_user_can_obtain_token(self):
        response = self.client.post(
            self.url,
            {
                'email': 'soft_deleted@test.com',
                'password': self.valid_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_inactive_user_cannot_obtain_token(self):
        response = self.client.post(
            self.url,
            {
                'email': 'inactive@test.com',
                'password': self.valid_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_existent_user(self):
        """Test authentication with non-existent user"""
        response = self.client.post(
            self.url,
            {
                'email': 'nonexistent@test.com',
                'password': self.valid_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_wrong_credentials(self):
        response = self.client.post(
            self.url,
            {
                'email': 'active@test.com',
                'password': 'wrongpassword'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_existent_user(self):
        response = self.client.post(
            self.url,
            {
                'email': 'nonexistent@test.com',
                'password': self.test_password
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_credentials(self):
        response = self.client.post(
            self.url,
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

