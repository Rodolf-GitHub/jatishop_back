from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import InfoNegocio, Categoria, Producto, NegocioUser
from ..serializers import (
    InfoNegocioSerializer,
    CategoriaSerializer,
    ProductoSerializer
)

class AdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @action(detail=False, methods=['get'])
    def my_business(self, request):
        """Obtener información del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = InfoNegocioSerializer(negocio)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_categories(self, request):
        """Obtener categorías del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        categorias = Categoria.objects.filter(negocio=negocio)
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Obtener productos del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        productos = Producto.objects.filter(
            subcategoria__categoria__negocio=negocio
        )
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data) 