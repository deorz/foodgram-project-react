from django.contrib import admin

from .models import Recipe, Ingredient, Tag, IngredientInRecipe, Favorite, \
    ShoppingCart


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    search_help_text = 'Название рецепта'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('ingredients')

    def author__username(self, obj):
        return obj.author.username


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    search_help_text = 'Название ингредиента'


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('slug',)


@admin.register(IngredientInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    list_filter = ('recipe',)
    search_fields = ('recipe__name',)
    search_help_text = 'Название рецепта'


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('user',)
    search_fields = ('user__name',)
    search_help_text = 'Имя пользователя'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('user',)
    search_fields = ('user__name',)
    search_help_text = 'Имя пользователя'
