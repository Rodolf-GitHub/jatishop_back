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
        exclude = ('negocio',)

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    subcategoria = SubcategoriaSerializer(read_only=True)
    subcategoria_id = serializers.PrimaryKeyRelatedField(
        source='subcategoria',
        queryset=Subcategoria.objects.all(),
        write_only=True
    )
    precio_con_descuento = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    tienda_nombre = serializers.SerializerMethodField()
    tienda_slug = serializers.SerializerMethodField()
    tienda_id = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_tienda_nombre(self, obj):
        return obj.subcategoria.categoria.negocio.nombre if obj.subcategoria and obj.subcategoria.categoria and obj.subcategoria.categoria.negocio else None

    def get_tienda_slug(self, obj):
        return obj.subcategoria.categoria.negocio.slug if obj.subcategoria and obj.subcategoria.categoria and obj.subcategoria.categoria.negocio else None

    def get_tienda_id(self, obj):
        return obj.subcategoria.categoria.negocio.id if obj.subcategoria and obj.subcategoria.categoria and obj.subcategoria.categoria.negocio else None

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

class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user