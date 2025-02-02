from django.urls import path
from rest_framework.routers import DefaultRouter
from ...views.admin_views.pedido_admin_views import AdminPedidoViewSet

router = DefaultRouter()
router.register('pedidos-admin', AdminPedidoViewSet, basename='admin-pedido')

urlpatterns = router.urls