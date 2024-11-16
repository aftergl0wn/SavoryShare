from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import baseconv
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .filter import RecipeCustomFilter
from .pagination import RecipePagination
from .permissions import OwnerOrReadOnly
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    RecordRecipeSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer
)
from .utils import util_favorite_shoppingcart
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag
)


User = get_user_model()


class AvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = AvatarSerializer
    lookup_field = 'avatar'

    def get_object(self):
        return self.request.user


class TagView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering = ('created_at',)
    filterset_class = RecipeCustomFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadRecipeSerializer
        return RecordRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        params = {
            'serializer': FavoriteSerializer,
            'base_model': Recipe,
            'related_model': Favorite
        }
        return util_favorite_shoppingcart(self, request, pk, params)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='shopping_cart')
    def shoppingcart(self, request, pk):
        params = {
            'serializer': ShoppingCartSerializer,
            'base_model': Recipe,
            'related_model': ShoppingCart
        }
        return util_favorite_shoppingcart(self, request, pk, params)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        encode_id = baseconv.base64.encode(recipe.id)
        short_link = request.build_absolute_uri(
            reverse('shortlink', kwargs={'encoded_id': encode_id})
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download(self, request):
        queryset = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(result_amount=Sum('amount'))
        list_shop = 'Список покупок:\n'
        for part in queryset:
            list_shop += (
                f'{part["ingredient__name"]}: {part["result_amount"]}'
                f'{part["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(list_shop, content_type='text/txt')
        response['Content-Disposition'] = (
            'attachment; filename="exported_data.txt"'
        )
        return response


class CustomUserViewSet(UserViewSet):
    pagination_class = RecipePagination

    @action(
        methods=['GET', 'PUT', 'PATCH', 'DELETE'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        queryset = self.request.user.subscribers.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        serializer = SubscribeSerializer(
            data={
                'user': self.request.user.id,
                'owner': get_object_or_404(User, id=id).id
            },
            context={'request': request})
        if request.method == "DELETE":
            if Subscribe.objects.filter(
                user=self.request.user.id,
                owner=get_object_or_404(User, id=id)
            ).exists():
                Subscribe.objects.get(
                    user=self.request.user,
                    owner=get_object_or_404(User, id=id)
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user,
            owner=get_object_or_404(User, id=id)
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['PUT', 'DELETE'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        serializer = AvatarSerializer(self.get_instance(), data=request.data)
        if request.method == "DELETE":
            self.request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShortLinkView(APIView):
    def get(self, request, encoded_id):
        if not set(encoded_id).issubset(set(baseconv.BASE64_ALPHABET)):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_id = baseconv.base64.decode(encoded_id)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(
                f'/recipes/{recipe.id}'
            )
        )
