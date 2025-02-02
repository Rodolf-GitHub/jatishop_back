from .marketplace_urls import urlpatterns as marketplace_urls
from .tienda_urls import urlpatterns as tienda_urls
from .auth_urls import urlpatterns as auth_urls
from .pedido_urls import urlpatterns as pedido_urls


urlpatterns = marketplace_urls + tienda_urls + auth_urls + pedido_urls

__all__ = ['urlpatterns'] 