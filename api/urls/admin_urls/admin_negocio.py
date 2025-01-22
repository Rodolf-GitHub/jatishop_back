from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.admin import AdminNegocioViewSet

router = DefaultRouter()
router.register('negocio', AdminNegocioViewSet, basename='admin-negocio')

urlpatterns = [
    path('', include(router.urls)),
] 