from django.contrib.auth import get_user_model
from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag


User = get_user_model()


class RecipeCustomFilter(FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.filter(recipe__isnull=False)
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.filter(tag_recipe__isnull=False),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value):
        if value is True and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is True and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset
