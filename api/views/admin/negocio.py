from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ...models import InfoNegocio, NegocioUser
from ...serializers import InfoNegocioSerializer

class AdminNegocioViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_negocio(self, user):
        try:
            negocio_user = NegocioUser.objects.get(user=user)
            return negocio_user.negocio
        except NegocioUser.DoesNotExist:
            return None

    @action(detail=False, methods=['post'])
    def create_business(self, request):
        """Crear un nuevo negocio para el usuario autenticado"""
        # Verificar si el usuario ya tiene un negocio
        if self.get_negocio(request.user):
            return Response(
                {'error': 'Ya tienes un negocio asociado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InfoNegocioSerializer(data=request.data)
        if serializer.is_valid():
            # Crear el negocio
            negocio = serializer.save()
            
            # Crear la relación NegocioUser
            NegocioUser.objects.create(
                user=request.user,
                negocio=negocio,
                es_propietario=True
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def my_business(self, request):
        """Gestionar información del negocio del usuario autenticado"""
        negocio = self.get_negocio(request.user)
        if not negocio:
            return Response(
                {'error': 'No tienes un negocio asociado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = InfoNegocioSerializer(negocio)
            return Response(serializer.data)
            
        elif request.method in ['PUT', 'PATCH']:
            serializer = InfoNegocioSerializer(
                negocio, 
                data=request.data, 
                partial=request.method=='PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            negocio.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 