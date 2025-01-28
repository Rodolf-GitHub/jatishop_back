from rest_framework import serializers
from ..models import Subcategoria, Producto, InfoNegocio
from .info_negocio_serializers import TiendaTemaSerializer

class NegocioReducidoSerializer(serializers.ModelSerializer):
    tema = TiendaTemaSerializer(read_only=True)
    
    class Meta:
        model = InfoNegocio
        fields = [
            'id',
            'nombre',
            'slug',
            'logo',
            'tema',
            'provincia',
            'municipio'
        ]

class ProductoSerializer(serializers.ModelSerializer):
    negocio = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'imagen',
            'descuento',
            'activo',
            'subcategoria',
            'precio_con_descuento',
            'created_at',
            'updated_at',
            'negocio'
        ]
        read_only_fields = ['id', 'precio_con_descuento', 'created_at', 'updated_at', 'negocio']

    def get_negocio(self, obj):
        negocio = obj.subcategoria.categoria.negocio
        return NegocioReducidoSerializer(negocio).data

    def validate_subcategoria(self, value):
        if not value:
            raise serializers.ValidationError("La subcategoría es requerida")
        return value