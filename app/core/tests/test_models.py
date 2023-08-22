"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models
from unittest.mock import patch


def create_user(email="user@example.com", password="pass1234"):
    """create and return a new user"""
    return get_user_model().objects.create_user(email,password)



class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test email is normalized"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """test that creating user an email raiser a vlalue error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """test create a super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'pass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_reciepe(self):
        """test creaitng a recipe in success"""

        user = get_user_model().objects.create_user(
            'test@examlpe.com',
            'pass1234'
        )

        receipe = models.Recipe.objects.create(
            user=user,
            title='sample recipe name',
            time_minitues=5,
            price=Decimal('5.50'),
            description='sample description'
        )

        self.assertEqual(str(receipe), receipe.title)


    def test_create_tag(self):
        """test creatng tag is success"""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name="tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_incredient(self):
        """test creating incrediant sucess"""
        user= create_user()
        incredient = models.Ingredient.objects.create(
            user=user,
            name="ingreadient"
        )

        self.assertEqual(str(incredient), incredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """test enereating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
