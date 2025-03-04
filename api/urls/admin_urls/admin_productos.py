from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.admin_views.producto_admin import AdminProductoViewSet

router = DefaultRouter()
router.register('productos', AdminProductoViewSet, basename='admin-productos')

urlpatterns = [
    path('', include(router.urls)),
] 