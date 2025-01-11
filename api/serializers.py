from rest_framework import serializers
from .models import *

class TiendaTemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiendaTema
        fields = ['color_primario', 'color_secundario']

class InfoNegocioSerializer(serializers.ModelSerializer):
    tema = TiendaTemaSerializer(read_only=True)

    class Meta:
        model = InfoNegocio
        fields = '__all__'

class NegocioUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegocioUser
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    precio_con_descuento = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Producto
        fields = '__all__'

# Serializers anidados para respuestas más completas
class SubcategoriaDetalleSerializer(SubcategoriaSerializer):
    productos = ProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Subcategoria
        fields = '__all__'

class CategoriaDetalleSerializer(CategoriaSerializer):
    subcategorias = SubcategoriaDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = '__all__'

class NegocioDetalleSerializer(InfoNegocioSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True, source='categoria_set')

    class Meta:
        model = InfoNegocio
        fields = '__all__'