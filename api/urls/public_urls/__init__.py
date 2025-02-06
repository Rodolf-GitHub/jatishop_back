from django.urls import path, include
from .marketplace_urls import urlpatterns as marketplace_urls
from .tienda_urls import urlpatterns as tienda_urls
from .auth_urls import urlpatterns as auth_urls
from .pedido_urls import urlpatterns as pedido_urls
from .licencia_urls import urlpatterns as licencia_urls

# Combinar todos los patrones de URL
urlpatterns = [
    path('marketplace/', include(marketplace_urls)),
    path('tienda/', include(tienda_urls)),
    path('auth/', include(auth_urls)),
    path('pedido/', include(pedido_urls)),
    path('licencia/', include(licencia_urls)),  # Asegúrate de que esta línea esté presente
]

__all__ = ['urlpatterns'] 