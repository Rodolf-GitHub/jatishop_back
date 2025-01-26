from rest_framework import serializers
from ..models import Categoria
from .subcategoria_serializers import SubcategoriaSerializer

class CategoriaAdminSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)
    negocio = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Categoria
        fields = '__all__'