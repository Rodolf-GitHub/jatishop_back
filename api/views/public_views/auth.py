from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ...serializers.user_auth_serializers import UserAuthSerializer
import logging
from drf_spectacular.utils import extend_schema
from ...models.negocio_models import NegocioUser

logger = logging.getLogger(__name__)

@extend_schema(
    tags=['auth'],
    description='Obtiene token de autenticación usando email o username'
)
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            # Obtener las credenciales
            username = request.data.get('username')
            password = request.data.get('password')

            logger.info(f"Intento de login con: {username}")

            # Si parece ser un email, buscar el usuario correspondiente
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                    logger.info(f"Email encontrado, username correspondiente: {username}")
                except User.DoesNotExist:
                    logger.warning(f"No se encontró usuario con email: {username}")
                    return Response({
                        'error': 'No existe usuario con ese email'
                    }, status=status.HTTP_404_NOT_FOUND)

            # Intentar autenticar al usuario
            user = authenticate(username=username, password=password)
            
            if user is None:
                logger.error(f"Autenticación fallida para usuario: {username}")
                return Response({
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Si la autenticación es exitosa, generar o recuperar el token
            token, created = Token.objects.get_or_create(user=user)
            
            # Obtener el negocio asociado al usuario si existe
            negocio_user = NegocioUser.objects.filter(user=user).first()
            negocio_data = None
            if negocio_user:
                negocio_data = {
                    'id': negocio_user.negocio.id,
                    'nombre': negocio_user.negocio.nombre,
                    'slug': negocio_user.negocio.slug
                }
            
            logger.info(f"Login exitoso para usuario: {user.username}")
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'username': user.username,
                'negocio': negocio_data
            })
            
        except Exception as e:
            logger.error(f"Error inesperado en login: {str(e)}")
            return Response({
                'error': 'Error en el proceso de autenticación',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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