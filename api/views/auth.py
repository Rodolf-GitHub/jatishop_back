from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from django.contrib.auth.models import User
from ..serializers import UserAuthSerializer
import logging
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)

@extend_schema(
    tags=['auth'],
    description='Obtiene token de autenticación usando email o username'
)
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Obtener las credenciales
        username = request.data.get('username')
        password = request.data.get('password')

        # Si parece ser un email, buscar el usuario correspondiente
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                return Response({
                    'error': 'No existe usuario con ese email'
                }, status=400)

        # Actualizar los datos de la solicitud con el username
        request.data['username'] = username

        # Continuar con el proceso normal de autenticación
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    if hasattr(request.user, 'auth_token'):
        request.user.auth_token.delete()
    return Response({'message': 'Sesión cerrada exitosamente'})

class UserAuthViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAuthSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserAuthSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error en registro de usuario: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes] 