from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ...models.negocio_models import InfoNegocio, NegocioUser
from ...serializers.info_negocio_serializers import InfoNegocioSerializer, NegocioDetalleSerializer
from ...utils.permissions import IsNegocioOwnerOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view

class InfoNegocioViewSet(viewsets.ModelViewSet):
    serializer_class = InfoNegocioSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsNegocioOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Si es una petición autenticada y tiene el token, no filtramos por activo
        if self.request.user and self.request.user.is_authenticated:
            queryset = InfoNegocio.objects.all()
        else:
            # Para vistas públicas, solo mostramos negocios activos
            queryset = InfoNegocio.objects.filter(activo=True)

        provincia = self.request.query_params.get('provincia')
        municipio = self.request.query_params.get('municipio')
        
        if provincia:
            queryset = queryset.filter(provincia=provincia)
            if municipio:
                queryset = queryset.filter(municipio=municipio)

        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )

        return queryset

    def get_object(self):
        queryset = InfoNegocio.objects.all()  # No filtramos por activo aquí
        negocio_slug = self.kwargs.get('slug')
        if negocio_slug is None:
            return super().get_object()
        
        obj = get_object_or_404(queryset, slug=negocio_slug)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NegocioDetalleSerializer
        return InfoNegocioSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            negocios = serializer.data
            for negocio in negocios:
                obj = queryset.get(id=negocio['id'])
                negocio['ubicacion'] = {
                    'provincia': obj.provincia,
                    'municipio': obj.municipio
                }
            return self.get_paginated_response(negocios)

        serializer = self.get_serializer(queryset, many=True)
        negocios = serializer.data
        for negocio in negocios:
            obj = queryset.get(id=negocio['id'])
            negocio['ubicacion'] = {
                'provincia': obj.provincia,
                'municipio': obj.municipio
            }
        return Response(negocios)

    def perform_create(self, serializer):
        negocio = serializer.save()
        NegocioUser.objects.create(
            user=self.request.user,
            negocio=negocio
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.propietario != self.request.user:
            raise PermissionDenied("No tienes permiso para modificar este negocio")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.propietario != self.request.user:
            raise PermissionDenied("No tienes permiso para eliminar este negocio")
        instance.delete()
