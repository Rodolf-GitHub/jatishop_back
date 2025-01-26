from rest_framework import serializers
from ..models import Subcategoria, Producto

class ProductoSerializer(serializers.ModelSerializer):
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