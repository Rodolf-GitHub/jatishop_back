from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .public_urls import marketplace_urls, tienda_urls, auth_urls
from .admin_urls import admin_urls

# Vista home simple
@api_view(['GET'])
def home_view(request):
    return Response({
        'message': 'Bienvenido a la API de JatiShop'
    })

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
    # Documentación API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Vista principal
    path('', home_view, name='home'),
    path('api/', api_root, name='api-root'),

    # URLs públicas
    path('', include(marketplace_urls)),
    path('', include(tienda_urls)),
    path('auth/', include(auth_urls)),

    # URLs de administración
    path('mi-negocio/', include(admin_urls)),
] 