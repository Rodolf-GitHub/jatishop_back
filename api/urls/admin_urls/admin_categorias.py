from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.admin_views.categoria_admin import AdminCategoriaViewSet

router = DefaultRouter()
router.register('categorias', AdminCategoriaViewSet, basename='admin-categorias')

urlpatterns = [
    path('', include(router.urls)),
] 