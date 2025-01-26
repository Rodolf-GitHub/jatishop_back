from django.db import models
from rest_framework import serializers
from ..models import InfoNegocio
from .tienda_tema_serializers import TiendaTemaSerializer
from .categoria_serializers import CategoriaSerializer
from django.db.models import Count, Sum

class InfoNegocioSerializer(serializers.ModelSerializer):
    tema = TiendaTemaSerializer(read_only=True)
    cantidad_productos = serializers.SerializerMethodField()

    class Meta:
        model = InfoNegocio
        fields = '__all__'

    def get_cantidad_productos(self, obj):
        return obj.categoria_set.annotate(
            productos_count=Count('subcategorias__productos', distinct=True)
        ).aggregate(
            total=Sum('productos_count')
        )['total'] or 0

class NegocioDetalleSerializer(InfoNegocioSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True, source='categoria_set')

    class Meta:
        model = InfoNegocio
        fields = '__all__' 