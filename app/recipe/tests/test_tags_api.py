"""Test for tags api"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def create_user(email='user@example,.com', password='pass1234'):
    """craete and return user"""
    return get_user_model().objects.create_user(email, password)

def detail_url(tag_id):
    """create and retun a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])

class PublicTagsAPITests(TestCase):
    """test case for un auth api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test auth is required for retrueving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITests(TestCase):
    """test authorized api reqs"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreived_tags(self):
        """test retreiveing a list of tags"""
        Tag.objects.create(user=self.user, name="vegan")
        Tag.objects.create(user=self.user, name="dessert")

        res=self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test list of tag limited to user"""

        user2 = create_user(email="yser@example.com")
        Tag.objects.create(user=user2, name="fruity")
        tag = Tag.objects.create(user=self.user, name="confirm")
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """updating a tag"""
        tag = Tag.objects.create(user=self.user, name="afetrt")
        payload = {
            "name": "updated name"
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """deletr tag"""
        tag = Tag.objects.create(user=self.user, name="afetrsdsdt")
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())