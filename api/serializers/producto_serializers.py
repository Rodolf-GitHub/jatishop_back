from rest_framework import serializers
from ..models import Subcategoria, Producto, InfoNegocio
from .info_negocio_serializers import TiendaTemaSerializer
from typing import Dict, Any
from decimal import Decimal

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
    negocio: Dict[str, Any] = serializers.SerializerMethodField()
    precio_con_descuento: float = serializers.FloatField(read_only=True)
    precio = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.00')
    )

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
        read_only_fields = [
            'id', 'precio_con_descuento', 
            'created_at', 'updated_at', 'negocio'
        ]

    def get_negocio(self, obj) -> Dict[str, Any]:
        negocio = obj.subcategoria.categoria.negocio
        return NegocioReducidoSerializer(negocio).data

    def validate_subcategoria(self, value):
        if not value:
            raise serializers.ValidationError("La subcategoría es requerida")
        return value