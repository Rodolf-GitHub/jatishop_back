from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from ...utils.ubicaciones_cuba import PROVINCIAS, get_municipios as get_municipios_cuba

class UbicacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()

class ProvinciasView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UbicacionSerializer
    
    def get(self, request):
        return Response(PROVINCIAS)

class MunicipiosView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UbicacionSerializer
    
    def get(self, request, provincia):
        municipios = get_municipios_cuba(provincia)
        if not municipios:
            return Response(
                {'error': f'No se encontraron municipios para la provincia {provincia}'}, 
                status=404
            )
        return Response(municipios)