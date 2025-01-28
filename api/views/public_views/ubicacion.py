from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ...utils.ubicaciones_cuba import PROVINCIAS, get_municipios as get_municipios_cuba

@api_view(['GET'])
@permission_classes([AllowAny])  # Explícitamente permitir acceso público
def get_provincias(request):
    return Response(PROVINCIAS)

@api_view(['GET'])
@permission_classes([AllowAny])  # Explícitamente permitir acceso público
def get_municipios(request, provincia):
    municipios = get_municipios_cuba(provincia)
    if not municipios:
        return Response(
            {'error': f'No se encontraron municipios para la provincia {provincia}'}, 
            status=404
        )
    return Response(municipios)