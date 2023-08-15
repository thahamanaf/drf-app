"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'Pass@123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'T@estpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_user(self):
        """test generates token for valid user"""
        user_details = {
            'name': "test name",
            'email': "test@example.com",
            'password': "testuser123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)




    def test_create_token_bad_credentials(self):
        """test retuirn error if cred is invalid"""

        create_user(email='test@example.com', password = 'goodpass')

        payload = { 'email': 'test@example.com', 'password': 'goofpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """test retiurn a blacn pass err"""

        payload = { 'email': 'test@excaxample.com', 'password': ''}

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """test authentication is requiered for user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """test api request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@examle.com",
            password='pass1234',
            name='testname'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving the profile for logges in user"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    def test_post_me_not_allowed(self):
        """test post is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """"test for updating the ser profile for authenticate user"""

        payload = {
            'name': "updated name",
            "password": "uodated password"
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
