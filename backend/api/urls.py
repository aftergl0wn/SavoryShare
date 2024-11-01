from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientView,
    MyUserViewSet,
    RecipeView,
    ShortLinkView,
    TagView
)

router = DefaultRouter()

router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('recipes', RecipeView, basename='recipes')
router.register('users', MyUserViewSet, basename='follow')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('s/<str:encoded_id>/', ShortLinkView.as_view(), name='shortlink')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
