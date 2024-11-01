from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response


def util_action(self, request, pk, findings):
    serializer = findings['serializer'](
        data={
            'user': self.request.user.pk,
            'recipe': pk},
        context={'request': request}
    )
    if request.method == "DELETE":
        if findings['related_model'].objects.filter(
            user=self.request.user,
            recipe=get_object_or_404(findings['base_model'], id=pk)
        ).exists():
            findings['related_model'].objects.get(
                user=self.request.user,
                recipe=get_object_or_404(findings['base_model'], id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.method == "POST":
        if serializer.is_valid():
            serializer.save(
                user=self.request.user,
                recipe=get_object_or_404(findings['base_model'], id=pk)
            )
            return Response(
                serializer.data.get('recipe'),
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def util_serializers(self, data, related_model):
    if related_model.objects.filter(
        user=self.initial_data.get('user'),
        recipe=int(self.initial_data.get('recipe'))
    ).exists():
        raise serializers.ValidationError(
            'Повторная подписка запрещена'
        )
    return data
