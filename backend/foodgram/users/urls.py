from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, SubscriptionsListView

app_name = 'users'

users_router = DefaultRouter()

users_router.register(r'users', UsersViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/subscriptions/',
        SubscriptionsListView.as_view(),
        name='subscriptions'
    ),
    path('', include(users_router.urls))
]
