from django.contrib.auth import get_user_model
from django.db import models

from .abstract_models import TagIngredient

User = get_user_model()

VALID_NAME_VALUES = 256
VALID_SLUG_VALUES = 32
VALID_UNIT_VALUES = 64


class Ingredient(TagIngredient):
    measurement_unit = models.CharField(
        max_length=VALID_UNIT_VALUES,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(TagIngredient):
    slug = models.SlugField(
        max_length=VALID_SLUG_VALUES,
        null=True,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        default_related_name = 'tag'
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner',
        verbose_name='Пользователь'
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'owner'],
                name='unique_user_owner'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return str(self.user)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображения'
    )
    name = models.CharField(
        max_length=VALID_NAME_VALUES,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    modified_at = models.DateTimeField(
        auto_now_add=False,
        auto_now=True,
        verbose_name='Дата редактирования'
    )
    REQUIRED_FIELDS = [
        'ingredients',
        'tags',
        'image',
        'name',
        'text',
        'cooking_time',
    ]

    class Meta:
        default_related_name = 'recipe'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return str(self.name)


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.user)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        verbose_name='Количество'
    )

    class Meta:
        default_related_name = 'ingredient_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты и рецепты'

    def __str__(self):
        return str(self.ingredient)


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = 'tag_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_recipe'
            )
        ]
        verbose_name = 'тег и рецепт'
        verbose_name_plural = 'Теги и рецепты'

    def __str__(self):
        return str(self.tag)


class Favorite(FavoriteShoppingCart):

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(FavoriteShoppingCart):

    class Meta:
        default_related_name = 'shoppingcart'
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
