from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from users.models import User
from utils.validators import min_value_validator


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name=_('Название')
    )
    color = models.CharField(
        max_length=7, unique=True, verbose_name=_('Цвет в HEX')
    )
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name=_('Уникальный слаг')
    )

    class Meta:
        db_table = 'tags'
        verbose_name = _('Тэг')
        verbose_name_plural = _('Тэги')
        ordering = ('slug',)

    def __str__(self):
        return '%s' % self.slug


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Название'))
    measurement_unit = models.CharField(
        max_length=200, verbose_name=_('Единицы измерения')
    )

    class Meta:
        db_table = 'ingredients'
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)

    def __str__(self):
        return '%s, %s' % (self.name, self.measurement_unit)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор')
    )
    name = models.CharField(max_length=200, verbose_name=_('Название'))
    image = models.ImageField(upload_to='recipes/', verbose_name=_('Картинка'))
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Список тэгов')
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('Время приготовления в минутах'),
        validators=(min_value_validator,)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name=_('Ингредиенты')
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True
    )

    class Meta:
        db_table = 'recipes'
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-pub_date',)

    def __str__(self):
        return '%s' % self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт')
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('Количество'),
        validators=(min_value_validator,)
    )

    class Meta:
        db_table = 'ingredients_in_recipe'
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецепте')
        ordering = ('amount',)
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            )
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )

    class Meta:
        db_table = 'favorites'
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        ordering = ('recipe',)
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )

    class Meta:
        db_table = 'shopping_cart'
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')
        ordering = ('recipe',)
