from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .views import (
    InfoNegocioViewSet,
    CategoriaViewSet,
    SubcategoriaViewSet,
    ProductoViewSet,
    MarketplaceProductoViewSet
)

# Router para el marketplace
marketplace_router = DefaultRouter()
marketplace_router.register(r'negocios', InfoNegocioViewSet)
marketplace_router.register(r'productos', MarketplaceProductoViewSet, basename='marketplace-productos')

@api_view(['GET'])
def api_root(request):
    return Response({
        'marketplace': {
            'descripcion': 'Endpoints del marketplace general',
            'url': f'{request.build_absolute_uri()}marketplace/'
        },
        'tiendas': {
            'descripcion': 'Endpoints específicos de tiendas',
            'ejemplo': f'{request.build_absolute_uri()}tienda/jatishop/'
        }
    })

urlpatterns = [
    # Vista raíz de la API
    path('', api_root, name='api-root'),

    # URLs del marketplace
    path('marketplace/', include(marketplace_router.urls)),

    # URLs específicas de cada tienda
    path('tienda/<slug:slug>/', include([
        path('', InfoNegocioViewSet.as_view({
            'get': 'retrieve'
        })),
        path('categorias/', CategoriaViewSet.as_view({
            'get': 'list'
        })),
        path('categorias/<int:pk>/', CategoriaViewSet.as_view({
            'get': 'retrieve'
        })),
        path('categorias/<int:pk>/detalles/', CategoriaViewSet.as_view({
            'get': 'detalles'
        })),
        path('subcategorias/', SubcategoriaViewSet.as_view({
            'get': 'list'
        })),
        path('subcategorias/<int:pk>/', SubcategoriaViewSet.as_view({
            'get': 'retrieve'
        })),
        path('productos/', ProductoViewSet.as_view({
            'get': 'list'
        })),
        path('productos/destacados/', ProductoViewSet.as_view({
            'get': 'destacados'
        })),
        path('productos/categoria/', ProductoViewSet.as_view({
            'get': 'por_categoria'
        })),
        path('productos/subcategoria/', ProductoViewSet.as_view({
            'get': 'por_subcategoria'
        })),
        path('productos/<int:pk>/', ProductoViewSet.as_view({
            'get': 'retrieve'
        })),
    ])),
]