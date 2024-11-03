from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import Recipe, ShoppingCart, Subscribe, Tag

User = get_user_model()


class TagBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField
    name = serializers.CharField
    slug = serializers.CharField

    class Meta:
        model = Tag
        fields = '__all__'


class UserBaseSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar',
                  'recipes',
                  'recipes_count')

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_authenticated is False:
            return False
        return Subscribe.objects.filter(
            user=self.context.get('request').user,
            owner=obj.id
        ).exists()


class FavoriteCartSerializerSPE(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ShoppingCartFavorite(serializers.ModelSerializer):
    recipe = FavoriteCartSerializerSPE(read_only=True)

    class Meta:
        fields = ('recipe',)
        model = ShoppingCart
