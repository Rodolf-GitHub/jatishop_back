from django.shortcuts import render

# Importaciones de las vistas modulares
from .views.negocio import InfoNegocioViewSet
from .views.producto import ProductoViewSet
from .views.categoria import CategoriaViewSet, SubcategoriaViewSet
from .views.marketplace import MarketplaceProductoViewSet
from .views.ubicacion import get_provincias, get_municipios
from .views.admin import (
    AdminNegocioViewSet,
    AdminCategoriaViewSet,
    AdminProductoViewSet
)

# Vista principal
def home_view(request):
    return render(request, 'api/home.html')

# Define explícitamente qué se exporta
__all__ = [
    'InfoNegocioViewSet',
    'ProductoViewSet',
    'CategoriaViewSet',
    'SubcategoriaViewSet',
    'MarketplaceProductoViewSet',
    'get_provincias',
    'get_municipios',
    'home_view',
    'AdminNegocioViewSet',
    'AdminCategoriaViewSet',
    'AdminProductoViewSet',
]