"""serializer for recipi api"""
from rest_framework import serializers
from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """serualizer for recipe"""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minitues', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """serilaizer for recipe view"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        