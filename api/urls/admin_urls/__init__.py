from .admin_negocio import urlpatterns as negocio_urls
from .admin_categorias import urlpatterns as categorias_urls
from .admin_productos import urlpatterns as productos_urls
from .pedido_admin_urls import urlpatterns as pedido_urls

urlpatterns = negocio_urls + categorias_urls + productos_urls + pedido_urls

__all__ = ['urlpatterns'] 