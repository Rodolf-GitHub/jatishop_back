from rest_framework import viewsets
from ..models import Categoria, Subcategoria, Producto

class BaseNegocioViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        negocio_slug = self.kwargs.get('slug')
        
        if self.queryset.model == Categoria:
            return qs.filter(negocio__slug=negocio_slug)
        elif self.queryset.model == Subcategoria:
            return qs.filter(categoria__negocio__slug=negocio_slug)
        elif self.queryset.model == Producto:
            return qs.filter(subcategoria__categoria__negocio__slug=negocio_slug)
        return qs