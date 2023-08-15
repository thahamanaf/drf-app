"""test recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """create and return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """crate and return recipe"""

    defaults = {
        'title': "sample recipe title",
        'time_minitues': 22,
        'price': Decimal('5.5'),
        'description': "sample descriton",
        'link': "http://example-recipe.com",

    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeAPITests(TestCase):
    """test iunauthenticated api test"""
    def setUp(self):
        self.client = APIClient()


    def test_auth_required_(self):
        """test auth req for api"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITest(TestCase):
    """test auth api reques"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """test retreiving list of recipe"""

        create_recipe(user = self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """test list of recipe to limited user"""
        other_user = get_user_model().objects.create_user('emaxple.com', 'pass1234')
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """tets get recipe details"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
