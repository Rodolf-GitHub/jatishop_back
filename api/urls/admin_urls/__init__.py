from .admin_negocio import urlpatterns as negocio_urls
from .admin_categorias import urlpatterns as categorias_urls
from .admin_productos import urlpatterns as productos_urls

urlpatterns = negocio_urls + categorias_urls + productos_urls

__all__ = ['urlpatterns'] 