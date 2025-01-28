from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ...views.public_views.marketplace import MarketplaceProductoViewSet
from ...views.public_views.negocio import InfoNegocioViewSet
from ...views.public_views.ubicacion import ProvinciasView, MunicipiosView

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
    path('ubicaciones/provincias/', ProvinciasView.as_view(), name='provincias'),
    path('ubicaciones/municipios/<str:provincia>/', MunicipiosView.as_view(), name='municipios'),

    # URLs del marketplace
    path('marketplace/', include(marketplace_router.urls)),
] 