from rest_framework import serializers
from ..models import Subcategoria, Producto

class ProductoSerializer(serializers.ModelSerializer):
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
            'updated_at'
        ]
        read_only_fields = ['id', 'precio_con_descuento', 'created_at', 'updated_at']

    def validate_subcategoria(self, value):
        if not value:
            raise serializers.ValidationError("La subcategoría es requerida")
        return value