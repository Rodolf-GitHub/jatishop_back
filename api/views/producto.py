from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import (
    Producto, 
    InfoNegocio
)
from ..serializers import ProductoSerializer
from .base import BaseNegocioViewSet
from ..pagination import ProductPagination
from ..permissions import IsNegocioOwnerOrReadOnly

class ProductoViewSet(BaseNegocioViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    pagination_class = ProductPagination
    permission_classes = [IsNegocioOwnerOrReadOnly]

    def perform_create(self, serializer):
        negocio = self.get_negocio()
        # La validación de permisos ya la hace IsNegocioOwnerOrReadOnly
        serializer.save()

    # Los métodos perform_update y perform_destroy ya no necesitan 
    # validación adicional porque la hace IsNegocioOwnerOrReadOnly