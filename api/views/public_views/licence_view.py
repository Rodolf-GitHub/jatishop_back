from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ...models import Licencia, InfoNegocio, NegocioUser
from ...serializers import LicenciaSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

class LicenciaEstadoView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener estado de licencia",
        description="Obtiene el estado actual de la licencia del negocio asociado al usuario autenticado",
        responses={
            200: OpenApiResponse(
                description="Estado de la licencia obtenido correctamente",
                response={
                    "type": "object",
                    "properties": {
                        "esta_activa": {
                            "type": "boolean",
                            "description": "Indica si la licencia está activa"
                        },
                        "dias_restantes": {
                            "type": "integer",
                            "description": "Días restantes de la licencia o días desde el vencimiento"
                        },
                        "fecha_vencimiento": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha de vencimiento de la licencia"
                        },
                        "negocio_activo": {
                            "type": "boolean",
                            "description": "Indica si el negocio está activo"
                        }
                    }
                }
            ),
            404: OpenApiResponse(
                description="Negocio o licencia no encontrada",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Mensaje de error"
                        }
                    }
                }
            )
        },
        tags=["Licencias"]
    )
    def get(self, request):
        try:
            # Obtener el usuario del negocio
            negocio_user = NegocioUser.objects.get(user=request.user)
            
            # Obtener el negocio asociado al usuario
            negocio = InfoNegocio.objects.get(usuarios=negocio_user)
            
            # Obtener la licencia del negocio
            licencia = Licencia.objects.get(negocio=negocio)
            
            # Verificar el estado actual de la licencia
            licencia.verificar_estado()
            
            # Preparar la respuesta
            data = {
                'esta_activa': licencia.esta_activa,
                'dias_restantes': licencia.dias_restantes,
                'fecha_vencimiento': licencia.fecha_vencimiento,
                'negocio_activo': negocio.activo
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except NegocioUser.DoesNotExist:
            return Response(
                {'error': 'No se encontró el usuario en el sistema'},
                status=status.HTTP_404_NOT_FOUND
            )
        except InfoNegocio.DoesNotExist:
            return Response(
                {'error': 'No se encontró un negocio asociado a este usuario'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Licencia.DoesNotExist:
            return Response(
                {'error': 'El negocio no tiene una licencia asignada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
