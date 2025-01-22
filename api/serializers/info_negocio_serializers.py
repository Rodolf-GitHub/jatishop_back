from rest_framework import serializers
from ..models import InfoNegocio
from .tienda_tema_serializers import TiendaTemaSerializer
from .categoria_serializers import CategoriaSerializer

class InfoNegocioSerializer(serializers.ModelSerializer):
    tema = TiendaTemaSerializer(read_only=True)

    class Meta:
        model = InfoNegocio
        fields = '__all__'

class NegocioDetalleSerializer(InfoNegocioSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True, source='categoria_set')

    class Meta:
        model = InfoNegocio
        fields = '__all__' 