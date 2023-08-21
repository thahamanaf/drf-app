"""test for ingredients"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL  = reverse("recipe:ingredient-list")

def detail_url(ingredient_id):
    """create and return an ingredient detaila url"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])

def create_user(email="email@example.com", password="pass1234"):
    """cratea and return a nrew user"""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientsAPITest(TestCase):
    """test for un auth api req"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        """test auth is req for retrirving data"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredietnsApiTest(TestCase):
    """test auth api req"""

    def setUp(self):
        self.user=create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_incredients(self):
        """tets get list of ingredients"""
        Ingredient.objects.create(user=self.user, name="kale")
        Ingredient.objects.create(user=self.user, name="vanila")

        res=self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """list of ingredient limited to auth user"""

        user2 = create_user(email="exampl2@example.com")
        Ingredient.objects.create(user=user2, name="salt")
        ingredient = Ingredient.objects.create(user=self.user, name="pepper")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_incredient(self):
        """test for update increcident"""
        ingredient = Ingredient.objects.create(user=self.user, name="selentr")
        payload = {"name": "coriender"}
        url = detail_url(ingredient.id)
        res=self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """test for deldete ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="lettus")
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())











