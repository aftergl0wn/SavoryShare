from django.contrib import admin

from .models import (
    Tag, Ingredient,
    Recipe, Subscribe,
    Favorite, ShoppingCart,
    IngredientRecipe, TagRecipe
)

admin.site.empty_value_display = 'Не задано'


class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeRecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'image',
        'name',
        'text',
        'cooking_time',
        'created_at',
        'modified_at',
        'favorite'
    )
    filter_horizontal = ('ingredients', 'tags')
    search_fields = ('name', 'author__email')
    list_filter = ('tags',)
    list_display_links = ('name',)
    inlines = (IngredientRecipeInline, TagRecipeRecipeInline)

    def favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    favorite.short_description = 'Количество добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )

    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscribe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
