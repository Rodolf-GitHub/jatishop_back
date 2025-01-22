from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.marketplace import MarketplaceProductoViewSet
from ...views.negocio import InfoNegocioViewSet
from ...views.ubicacion import get_provincias, get_municipios

# Router para el marketplace
marketplace_router = DefaultRouter()
marketplace_router.register(
    r'negocios', 
    InfoNegocioViewSet,
    basename='marketplace-negocios'
)
marketplace_router.register(
    r'productos', 
    MarketplaceProductoViewSet, 
    basename='marketplace-productos'
)

urlpatterns = [
    # URLs de ubicaciones
    path('ubicaciones/provincias/', get_provincias, name='provincias'),
    path('ubicaciones/municipios/<str:provincia>/', get_municipios, name='municipios'),

    # URLs del marketplace
    path('marketplace/', include(marketplace_router.urls)),
] 