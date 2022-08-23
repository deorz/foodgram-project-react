from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagsViewSet, IngredientsViewSet, RecipesViewSet

app_name = 'recipes'

recipes_router = DefaultRouter()
recipes_router.register(r'tags', TagsViewSet)
recipes_router.register(r'ingredients', IngredientsViewSet)
recipes_router.register(r'recipes', RecipesViewSet)

urlpatterns = [
    path('', include(recipes_router.urls))
]
