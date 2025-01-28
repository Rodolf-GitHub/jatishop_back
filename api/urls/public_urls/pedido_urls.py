from django.urls import path
from rest_framework.routers import DefaultRouter
from ...views.public_views.pedido_views import PedidoViewSet

router = DefaultRouter()
router.register('', PedidoViewSet, basename='pedido')

urlpatterns = [
    # Rutas adicionales específicas si las necesitas
] + router.urls