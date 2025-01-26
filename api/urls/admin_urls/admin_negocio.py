from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.admin_views.negocio_admin import AdminNegocioViewSet

router = DefaultRouter()
router.register('negocio', AdminNegocioViewSet, basename='admin-negocio')

urlpatterns = [
    path('', include(router.urls)),
    path('resumen/', AdminNegocioViewSet.as_view({'get': 'get_resumen'}), name='admin-resumen'),
] 