from django.urls import path,include
from rest_framework.routers import DefaultRouter
from ...views.public_views.pedido_views import PedidoViewSet

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedidos')

urlpatterns = router.urls