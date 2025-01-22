from rest_framework import serializers
from ..models import Categoria
from .subcategoria_serializers import SubcategoriaDetalleSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        exclude = ('negocio',)

class CategoriaDetalleSerializer(CategoriaSerializer):
    subcategorias = SubcategoriaDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = '__all__' 