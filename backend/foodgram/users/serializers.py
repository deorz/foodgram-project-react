from django.contrib.auth.hashers import make_password, check_password
from django.core import validators
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from .models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=(validators.RegexValidator(regex=r'^[\w.@+-]+\Z'),)
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'password', 'is_subscribed'
        )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            False if user.is_anonymous else
            Subscription.objects.filter(subscriber=user, author=obj).exists()
        )


class UserSetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=150, write_only=True)
    current_password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def update(self, instance, validated_data):
        if not check_password(
                validated_data.get('current_password'), instance.password
        ):
            raise ValidationError({'error': _('Неверный пароль')})
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('user', 'recipes', 'recipes_count')

    def get_user(self, obj):
        author = obj.author
        return UserSerializer(author, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.author.recipe_set.count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = (
            obj.author.recipe_set.all() if not recipes_limit
            else obj.author.recipe_set.all()[:int(recipes_limit)]
        )
        return RecipeMinifiedSerializer(recipes, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = data.pop('user')
        for key, value in user.items():
            data.update({key: value})
        data.move_to_end('recipes')
        data.move_to_end('recipes_count')
        return data
