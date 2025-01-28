from django.urls import path
from rest_framework.routers import DefaultRouter
from ...views.public_views.auth import CustomAuthToken, LogoutView, UserAuthViewSet

router = DefaultRouter()
router.register('', UserAuthViewSet, basename='user')

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view(), name='api_token_logout'),
    path('register/', UserAuthViewSet.as_view({'post': 'create'}), name='user_register'),
    path('me/', UserAuthViewSet.as_view({'get': 'me'}), name='user_me'),
    path('change-password/', UserAuthViewSet.as_view(
        {'post': 'change_password'}
    ), name='user_change_password'),
] + router.urls