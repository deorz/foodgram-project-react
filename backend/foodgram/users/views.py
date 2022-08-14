from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin

from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User, Subscription
from .serializers import (
    UserSerializer, UserSetPasswordSerializer, SubscriptionSerializer
)


class UsersViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return AllowAny(),
        return super().get_permissions()

    @action(methods=['GET'], detail=False, url_path='me', url_name='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_path='set_password',
            url_name='set_password')
    def set_password(self, request):
        user = request.user
        serializer = UserSetPasswordSerializer(
            instance=user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(
            instance=user,
            validated_data=serializer.validated_data
        )
        return Response(data={'info': 'Пароль успешно изменён'})

    @action(methods=['POST'], detail=True, url_path='subscribe',
            url_name='subscribe')
    def subscribe(self, request, pk=None):
        subscriber = self.request.user
        author = get_object_or_404(User, id=pk)
        if subscriber.id == author.id:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(
                subscriber=subscriber, author=author
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = Subscription.objects.create(
            subscriber=subscriber, author=author
        )
        return Response(SubscriptionSerializer(
            subscription, context=self.get_serializer_context()
        ).data)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk=None):
        subscriber = self.request.user
        author = get_object_or_404(User, id=pk)
        if subscriber.id == author.id:
            return Response(
                {'error': 'Нельзя отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Subscription.objects.filter(
                subscriber=subscriber, author=author
        ).exists():
            return Response(
                {'error': 'Вы не были подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.filter(
            subscriber=subscriber, author=author
        ).delete()
        return Response(
            {'info': 'Вы успешно отписались от пользователя'},
            status=status.HTTP_204_NO_CONTENT
        )


class SubscriptionsListView(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Subscription.objects.filter(
            subscriber=self.request.user
        ).select_related('author').all()
