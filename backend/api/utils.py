from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response


def util_favorite_shoppingcart(self, request, pk, param):
    serializer = param['serializer'](
        data={
            'user': self.request.user.pk,
            'recipe': get_object_or_404(param['base_model'], id=pk).pk},
        context={'request': request}
    )
    if request.method == "DELETE":
        if param['related_model'].objects.filter(
            user=self.request.user,
            recipe=get_object_or_404(param['base_model'], id=pk)
        ).exists():
            param['related_model'].objects.get(
                user=self.request.user,
                recipe=get_object_or_404(param['base_model'], id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        user=self.request.user,
        recipe=get_object_or_404(param['base_model'], id=pk)
    )
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


def util_validate_recipe_subscriptions(self, data, related_model):
    if related_model.objects.filter(
        user=data.get('user'),
        recipe=data.get('recipe')
    ).exists():
        raise serializers.ValidationError(
            'Повторная подписка запрещена'
        )
    return data


def util_favorited_shopping_cart(self, obj, base_model):
    if not self.context.get('request').user.is_authenticated:
        return False
    return base_model.objects.filter(
        user=self.context.get('request').user,
        recipe=obj.id
    ).exists()
