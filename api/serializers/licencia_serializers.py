from rest_framework import serializers
from ..models import Licencia


class LicenciaSerializer(serializers.ModelSerializer):
    dias_restantes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Licencia
        fields = [
            'id', 'negocio', 'fecha_inicio', 'fecha_vencimiento',
            'esta_activa', 'dias_restantes'
        ]