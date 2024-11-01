import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe, ShoppingCart, Subscribe, Tag

User = get_user_model()


class TagBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField
    name = serializers.CharField
    slug = serializers.CharField

    class Meta:
        model = Tag
        fields = '__all__'


class MyUserBaseSerializer(UserSerializer):
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
        if self.context.get('request').user.is_authenticated:
            return Subscribe.objects.filter(
                user=self.context.get('request').user,
                owner=obj.id
            ).exists()
        return False


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
