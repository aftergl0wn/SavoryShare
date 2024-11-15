from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient,
    IngredientRecipe, Recipe,
    ShoppingCart, Subscribe,
    Tag, TagRecipe
)
from .mixins import (
    Base64ImageField, ShoppingCartFavorite,
    TagBaseSerializer, UserBaseSerializer,
)
from .utils import (
    util_favorited_shopping_cart,
    util_validate_recipe_subscriptions
)

User = get_user_model()


class TagSerializerSPE(TagBaseSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.CharField(source='tag.name')
    slug = serializers.CharField(source='tag.slug')


class TagSerializer(TagBaseSerializer):
    pass


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class WriteIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class BaseUserSerializer(UserBaseSerializer):

    class Meta(UserBaseSerializer.Meta):
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializerSPE(UserBaseSerializer):
    email = serializers.ReadOnlyField(source='owner.email')
    id = serializers.ReadOnlyField(source='owner.id')
    username = serializers.ReadOnlyField(source='owner.username')
    first_name = serializers.ReadOnlyField(source='owner.first_name')
    last_name = serializers.ReadOnlyField(source='owner.last_name')
    avatar = Base64ImageField(source='owner.avatar')
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        url = self.context.get('request').build_absolute_uri()
        if 'recipes_limit' in url:
            url, number = url.split('recipes_limit=')
            return Recipe.objects.filter(
                author=obj.owner
            )[:int(number)].count()
        return Recipe.objects.filter(author=obj.id).count()

    def get_recipes(self, obj):
        url = self.context.get('request').build_absolute_uri()
        if 'recipes_limit' in url:
            url, number = url.split('recipes_limit=')
            return RecipeSerializer(
                Recipe.objects.filter(author=obj.owner)[:int(number)],
                many=True
            ).data
        return RecipeSerializer(
            Recipe.objects.filter(author=obj.owner),
            many=True
        ).data


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('owner', 'user')
        model = Subscribe

    def validate(self, data):
        if data.get(
            'user'
        ) == data.get('owner'):
            raise serializers.ValidationError(
                'Подписка на свой аккаунт запрещена'
            )
        return data

    def to_representation(self, instance):
        return SubscribeSerializerSPE(instance, context=self.context).data


class ReadRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = BaseUserSerializer(read_only=True)
    tags = TagSerializerSPE(many=True, source='tags_recipes')
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        return util_favorited_shopping_cart(self, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return util_favorited_shopping_cart(self, obj, ShoppingCart)


class RecordRecipeSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Tag.objects.all()
    )
    ingredients = WriteIngredientRecipeSerializer(
        many=True,
        required=True,
        source='ingredients_recipes'
    )
    cooking_time = serializers.IntegerField()

    def validate(self, data):
        if not {'ingredients_recipes', 'tags'}.issubset(data):
            raise serializers.ValidationError(
                'Поля ingredients и tags должно быть указаны'
            )
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле ingredients должно быть заполнено'
            )
        list_id = []
        for part_value in value:
            if Ingredient.objects.filter(
                id=part_value['id']
            ).exists() is False or part_value['amount'] < 1:
                raise serializers.ValidationError(
                    'Некорректное поле ingredients/amount'
                )
            list_id.append(part_value['id'])
        if len(list_id) != len(set(list_id)):
            raise serializers.ValidationError(
                'Добавление повторяющихся ingredients запрещено'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле tags должно быть заполнено'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Добавление повторяющихся tags запрещено'
            )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Некорректное поле cooking_time, должно быть больше 1'
            )
        return value

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )
        read_only_fields = ('author',)

    def split_validated_data(self, validated_data):
        return (
            dict.pop(validated_data, 'ingredients_recipes'),
            dict.pop(validated_data, 'tags')
        )

    def create(self, validated_data):
        ingredients, tags = self.split_validated_data(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient_id=ingredient.get("id"),
                recipe=recipe,
                amount=ingredient.get("amount")
            ) for ingredient in ingredients
        )
        TagRecipe.objects.bulk_create(
            TagRecipe(
                tag=get_object_or_404(Tag, id=tag.id),
                recipe=recipe
            )for tag in tags
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients, tags = self.split_validated_data(validated_data)
        super().update(instance, validated_data)
        IngredientRecipe.objects.filter(
            recipe=instance.id
        ).delete()
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient_id=ingredient.get("id"),
                recipe_id=instance.id,
                amount=ingredient.get("amount")
            ) for ingredient in ingredients
        )
        old_tags = set(instance.tags.values_list('id', flat=True))
        new_tags = set(tag.id for tag in tags)
        TagRecipe.objects.filter(
            recipe=instance.id,
            tag__in=old_tags - new_tags
        ).delete()
        TagRecipe.objects.bulk_create(
            TagRecipe(
                tag=get_object_or_404(Tag, id=tag),
                recipe=instance
            ) for tag in (new_tags - old_tags)
        )
        return instance

    def to_representation(self, value):
        return ReadRecipeSerializer(instance=value, context=self.context).data


class FavoriteSerializer(ShoppingCartFavorite):

    class Meta(ShoppingCartFavorite.Meta):
        model = Favorite

    def validate(self, data):
        return util_validate_recipe_subscriptions(self, data, Favorite)


class ShoppingCartSerializer(ShoppingCartFavorite):

    def validate(self, data):
        return util_validate_recipe_subscriptions(self, data, ShoppingCart)
