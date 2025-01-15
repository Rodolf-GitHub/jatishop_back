from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..ubicaciones_cuba import PROVINCIAS, get_municipios as get_municipios_cuba

@api_view(['GET'])
def get_provincias(request):
    return Response(PROVINCIAS)

@api_view(['GET'])
def get_municipios(request, provincia):
    municipios = get_municipios_cuba(provincia)
    if not municipios:
        return Response(
            {'error': f'No se encontraron municipios para la provincia {provincia}'}, 
            status=404
        )
    return Response(municipios)