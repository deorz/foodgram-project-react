from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from utils.functions import check_exists_and_create_or_delete, get_object
from utils.permissions import IsAuthorOrReadOnly
from utils.filters import IngredientSearchFilter, RecipeFilterSet
from users.serializers import RecipeMinifiedSerializer
from .models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeViewSerializer,
    RecipeWriteSerializer
)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


@method_decorator(transaction.atomic, name='create')
@method_decorator(transaction.atomic, name='update')
class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags', 'ingredientinrecipe_set'
    ).all()
    serializer_class = RecipeViewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'destroy'):
            return RecipeWriteSerializer
        return super().get_serializer_class()

    @action(methods=['POST'], detail=True, url_name='favorite',
            url_path='favorite', permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user, recipe = get_object(request=request, object_model=Recipe, pk=pk)
        check_exists_and_create_or_delete(
            object_model=Favorite, exists=True,
            msg='Рецепт уже есть в избранном',
            user=user, recipe=recipe
        )
        serializer = RecipeMinifiedSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user, recipe = get_object(request=request, object_model=Recipe, pk=pk)
        check_exists_and_create_or_delete(
            object_model=Favorite, exists=False,
            msg='Рецепт не был добавлен в избранное',
            user=user, recipe=recipe
        )
        return Response(
            {'info': 'Рецепт успешно удалён из избранного'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['POST'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user, recipe = get_object(request=request, object_model=Recipe, pk=pk)
        check_exists_and_create_or_delete(
            object_model=ShoppingCart, exists=True,
            msg='Рецепт уже есть в списке покупок',
            user=user, recipe=recipe
        )
        serializer = RecipeMinifiedSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user, recipe = get_object(request=request, object_model=Recipe, pk=pk)
        check_exists_and_create_or_delete(
            object_model=ShoppingCart, exists=False,
            msg='Рецепт не был добавлен в список покупок',
            user=user, recipe=recipe
        )
        return Response(
            {'info': 'Рецепт успешно удалён из списка покупок'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = Ingredient.objects.filter(
            recipe__shoppingcart__user=user
        ).prefetch_related(
            'recipe_set', 'ingredientinrecipe_set'
        ).annotate(
            ingredient_amount=Sum('ingredientinrecipe__amount')
        ).values_list('name', 'measurement_unit', 'ingredient_amount')
        pdfmetrics.registerFont(
            TTFont(
                'SF-Pro',
                Path(settings.DATA_ROOT, 'fonts/SF-Pro.ttf'), 'UTF-8'
            )
        )
        response = HttpResponse(content_type='application/pdf')
        filename = 'shopping_list.pdf'
        response['Content-Disposition'] = (
                'attachment; filename="%s"' % filename
        )
        file = canvas.Canvas(response, pagesize=A4)
        file.setFont('SF-Pro', size=24)
        file.drawString(200, 800, 'Список покупок')
        file.setFont('SF-Pro', size=16)
        height = 750
        for index, (name, unit, amount) in enumerate(ingredients, 1):
            file.drawString(
                75, height, '%d. %s (%s) - %s' % (
                    index, name, unit, amount
                )
            )
            height -= 25
        file.showPage()
        file.save()
        return response
