from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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

from utils.permissions import IsAuthorOrReadOnly
from utils.filters import IngredientSearchFilter, RecipeFilterSet
from users.serializers import RecipeMinifiedSerializer
from .models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientInRecipe
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


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
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
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже есть в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            {'info': 'Рецепт успешно удалён из избранного'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['POST'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            {'info': 'Рецепт успешно удалён из списка покупок'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shoppingcart__user=user
        ).select_related('ingredient').all().values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount'
        )
        shopping_cart = dict()
        for ingredient in ingredients:
            name, measurement_unit, amount = ingredient
            if name in shopping_cart:
                shopping_cart[name]['amount'] += amount
            else:
                shopping_cart[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
        pdfmetrics.registerFont(
            TTFont(
                'SF-Pro',
                Path(settings.BASE_DIR).resolve().parent.parent.joinpath(
                    'data/fonts/SF-Pro.ttf'
                ), 'UTF-8'
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
        for index, (name, ingredient) in enumerate(shopping_cart.items(), 1):
            measurement_unit = ingredient['measurement_unit']
            amount = ingredient['amount']
            file.drawString(
                75, height, '%d. %s (%s) - %s' % (
                    index, name, measurement_unit, amount
                )
            )
            height -= 25
        file.showPage()
        file.save()
        return response
