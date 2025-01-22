from rest_framework import serializers
from ..models import TiendaTema

class TiendaTemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiendaTema
        fields = ['color_primario', 'color_secundario'] 