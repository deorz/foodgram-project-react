from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer
from utils.validators import min_value_validator
from .models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientInRecipe
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeViewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.select_related(
            'ingredient', 'recipe'
        ).filter(recipe=obj).all()
        return IngredientInRecipeSerializer(
            ingredients, context=self.context, many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            False if user.is_anonymous else
            Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            False if user.is_anonymous else
            ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                {'error': 'Для рецепта необходим хотя бы один ингредиент'}
            )
        ingredient_list = set()
        for ingredient_ in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ingredient_['id'])
            ingredient_list.add(ingredient)
            min_value_validator(int(ingredient_['amount']))
        attrs['ingredients'] = ingredients
        return attrs

    def create_ingredients(self, ingredients, recipe):
        for inredient in ingredients:
            IngredientInRecipe.objects.create(
                ingredient_id=inredient['id'], recipe=recipe,
                amount=inredient['amount']
            )

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.add(*tags)
        self.create_ingredients(ingredients=ingredients, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        print(validated_data)
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        instance.tags.add(*tags)
        self.create_ingredients(ingredients=ingredients, recipe=recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeViewSerializer(instance, context=self.context).data
