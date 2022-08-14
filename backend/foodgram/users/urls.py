from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, SubscriptionsListView

app_name = 'users'

users_router = DefaultRouter()

users_router.register(r'users', UsersViewSet)

urlpatterns = [
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path(
        'api/users/subscriptions/',
        SubscriptionsListView.as_view(),
        name='subscriptions'
    ),
    path('api/', include(users_router.urls))
]
