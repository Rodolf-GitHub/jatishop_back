from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..ubicaciones_cuba import PROVINCIAS, get_municipios as get_municipios_cuba
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from rest_framework import serializers

@extend_schema(
    tags=['ubicaciones'],
    description='Obtener lista de provincias de Cuba',
    responses={
        200: inline_serializer(
            name='ProvinciasResponse',
            fields={
                'provincias': serializers.ListField(child=serializers.CharField())
            }
        )
    },
    examples=[
        OpenApiExample(
            'Ejemplo de respuesta',
            value=['La Habana', 'Santiago de Cuba', 'Pinar del Río']
        )
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_provincias(request):
    return Response(PROVINCIAS)

@extend_schema(
    tags=['ubicaciones'],
    description='Obtener municipios de una provincia específica',
    parameters=[
        OpenApiParameter(
            name='provincia',
            type=str,
            location=OpenApiParameter.PATH,
            description='Nombre de la provincia'
        )
    ],
    responses={
        200: inline_serializer(
            name='MunicipiosResponse',
            fields={
                'municipios': serializers.ListField(child=serializers.CharField())
            }
        ),
        404: inline_serializer(
            name='ErrorResponse',
            fields={
                'error': serializers.CharField()
            }
        )
    },
    examples=[
        OpenApiExample(
            'Ejemplo de respuesta exitosa',
            value=['Plaza', 'Centro Habana', 'Habana Vieja']
        )
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_municipios(request, provincia):
    municipios = get_municipios_cuba(provincia)
    if not municipios:
        return Response(
            {'error': f'No se encontraron municipios para la provincia {provincia}'}, 
            status=404
        )
    return Response(municipios)