from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsNegocioOwnerOrReadOnly
from ..models import Categoria, Subcategoria, Producto, InfoNegocio

class BaseNegocioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsNegocioOwnerOrReadOnly]
    
    def get_queryset(self):
        negocio_slug = self.kwargs.get('negocio_slug')
        if not negocio_slug:
            return self.queryset.none()
        
        return self.queryset.filter(
            negocio__slug=negocio_slug
        )

    def perform_create(self, serializer):
        negocio_slug = self.kwargs.get('negocio_slug')
        negocio = InfoNegocio.objects.get(slug=negocio_slug)
        serializer.save(negocio=negocio)