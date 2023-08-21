"""test recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
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

def create_user(**params):
    return get_user_model().objects.create_user(**params)

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
        self.user = create_user(email="user@example.com", password="pass1234")

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
        other_user = create_user(email='emil@emaxple.com', password='pass1234')
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
            'time_minitues': 30,
            'price': Decimal('5.99'),
            'description': "asdas"
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """test partial update of the recipe"""
        original_link = "htps://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="ssamlple",
            link=original_link
        )

        payload = {
            "title": "new title",
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        original_link = "htps://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="ssamlple",
            link=original_link,
            description = "descr"
        )

        payload = {
            "title": "new title",
            "link": "http://example/new",
            "description": "new desc",
            "time_minitues" :10,
            "price": Decimal("4.3")
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """test to chek user return err"""

        new_user = create_user(email='email2@ecxample.com', password='pass134')
        recipe = create_recipe(user=self.user)
        payload = {
            "user": new_user.id
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """test delete recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res= self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_other_users_recipe_error(self):
        new_user = create_user(email='email2@ecxample.com', password='pass134')
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res= self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_craete_recipe_with_new_tags(self):
        """cratinga rrecupi with tags """
        payload = {
            "title": "thai curry",
            "time_minitues": 30,
            "price": Decimal("5.5"),
            "tags": [
                {"name": "thair"},
                {"name": "Dinner"},
            ],
            "description": "dummy descriptioj"
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """test creating recipe with existing tag"""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Pongal",
            "time_minitues": 30,
            "price": "23",
            "description": "descripiton",
            "tags": [
                {"name": "Indian"},
                {"name": "Breakfast"},
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """test create tag when updating a recipe"""
        recipe = create_recipe(user=self.user)
        payload = { "tags": [{"name": "lunch"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name="lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """assiging an exisinting tag when updadig recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name="breakfast")
        recipe=create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="lunch")
        payload = { "tags": [{"name": "lunch"}]}
        url =detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """test clearung recipe trags"""
        tag = Tag.objects.create(user=self.user, name="desert")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {"tags" : []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_reacipe_with_ingredient(self):
        """test for creating ingrediants"""

        payload = {"title": "coulifflower", "time_minitues": 30, "price": "5.5", "ingredients": [
            {"name": "calufiflower"}, {"name": "sale"}
        ], "description": "dwed"}

        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """test for creating recipe with exisitng ingredient"""

        ingredient = Ingredient.objects.create(user= self.user, name="loiuy")

        payload = {
            "title": "htyye",
            "time_minitues": 23,
            "description": "dwed",
            "price": "3.2",
            "ingredients": [
                {"name":"jasdhsad"},
                {"name":"loiuy"}
            ]
        }

        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingreient in payload['ingredients']:
            exists = recipe.ingredients.filter(
            name=ingreient['name'],
            user=self.user
            ).exists()
            self.assertTrue(exists)









