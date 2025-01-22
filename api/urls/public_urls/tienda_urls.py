from django.urls import path
from ...views.negocio import InfoNegocioViewSet
from ...views.producto import ProductoViewSet
from ...views.categoria import CategoriaViewSet, SubcategoriaViewSet

urlpatterns = [
    # URLs específicas de cada tienda
    path('tienda/<slug:slug>/', include([
        path('', InfoNegocioViewSet.as_view({
            'get': 'retrieve'
        })),
        path('productos/', ProductoViewSet.as_view({
            'get': 'list'
        })),
        path('productos/<int:pk>/', ProductoViewSet.as_view({
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
        path('productos/categoria/', ProductoViewSet.as_view({
            'get': 'por_categoria'
        })),
        path('productos/subcategoria/', ProductoViewSet.as_view({
            'get': 'por_subcategoria'
        })),
    ])),
] 