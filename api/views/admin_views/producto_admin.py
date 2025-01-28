from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view
from ...models import Producto, NegocioUser
from ...serializers import ProductoSerializer

class AdminProductoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @action(detail=False, methods=['get', 'post'])
    def my_products(self, request):
        print("DEBUG - Método:", request.method)
        print("DEBUG - Data recibida:", request.data)
        
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            productos = Producto.objects.filter(
                subcategoria__categoria__negocio=negocio
            ).select_related(
                'subcategoria',
                'subcategoria__categoria'
            ).values(
                'id', 'nombre', 'descripcion', 'precio', 'stock', 'imagen', 'descuento', 'activo',
                'subcategoria__id', 'subcategoria__nombre',
                'subcategoria__categoria__id', 'subcategoria__categoria__nombre'
            )
            
            # Formatear la respuesta
            productos_formateados = []
            for producto in productos:
                productos_formateados.append({
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'descripcion': producto['descripcion'],
                    'precio': producto['precio'],
                    'stock': producto['stock'],
                    'imagen': producto['imagen'],
                    'descuento': producto['descuento'],
                    'activo': producto['activo'],
                    'subcategoria': {
                        'id': producto['subcategoria__id'],
                        'nombre': producto['subcategoria__nombre'],
                        'categoria': {
                            'id': producto['subcategoria__categoria__id'],
                            'nombre': producto['subcategoria__categoria__nombre']
                        }
                    }
                })
            return Response(productos_formateados)
            
        elif request.method == 'POST':
            print("DEBUG - Procesando POST")
            serializer = ProductoSerializer(data=request.data)
            
            if serializer.is_valid():
                # Verificar que la subcategoría pertenece al negocio
                subcategoria = serializer.validated_data['subcategoria']
                if subcategoria.categoria.negocio != negocio:
                    return Response(
                        {'error': 'La subcategoría no pertenece a tu negocio'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                producto = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            print("DEBUG - Errores del serializer:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            producto = Producto.objects.get(
                pk=pk,
                subcategoria__categoria__negocio=negocio
            )
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductoSerializer(producto, data=request.data)
        if serializer.is_valid():
            if 'subcategoria' in serializer.validated_data:
                subcategoria = serializer.validated_data['subcategoria']
                if subcategoria.categoria.negocio != negocio:
                    return Response(
                        {'error': 'La subcategoría no pertenece a tu negocio'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch'])
    def update_product(self, request, pk=None):
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            producto = Producto.objects.get(
                pk=pk,
                subcategoria__categoria__negocio=negocio
            )
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductoSerializer(
            producto,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            if 'subcategoria' in serializer.validated_data:
                subcategoria = serializer.validated_data['subcategoria']
                if subcategoria.categoria.negocio != negocio:
                    return Response(
                        {'error': 'La subcategoría no pertenece a tu negocio'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer.save()
            print("DEBUG - Response data:", serializer.data)  # Agregado para depuración
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_product(self, request, pk=None):
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            producto = Producto.objects.get(
                pk=pk,
                subcategoria__categoria__negocio=negocio
            )
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        producto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)