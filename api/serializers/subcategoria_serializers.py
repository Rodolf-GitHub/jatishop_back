from rest_framework import serializers
from ..models import Subcategoria
from .producto_serializers import ProductoSerializer

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = '__all__'

class SubcategoriaDetalleSerializer(SubcategoriaSerializer):
    productos = ProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Subcategoria
        fields = '__all__' 