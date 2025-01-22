from rest_framework import serializers
from ..models import NegocioUser

class NegocioUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegocioUser
        fields = '__all__' 