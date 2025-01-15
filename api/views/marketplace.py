from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from collections import OrderedDict
from urllib.parse import urlencode
from ..models import Producto
from ..serializers import ProductoSerializer
from ..pagination import ProductPagination

class MarketplaceProductoViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               GenericViewSet):
    serializer_class = ProductoSerializer
    pagination_class = ProductPagination
    
    def get_queryset(self):
        queryset = Producto.objects.filter(
            activo=True,
            subcategoria__categoria__negocio__activo=True
        ).select_related(
            'subcategoria__categoria__negocio'
        ).order_by('-created_at')

        provincia = self.request.query_params.get('provincia')
        municipio = self.request.query_params.get('municipio')
        
        if provincia:
            queryset = queryset.filter(
                subcategoria__categoria__negocio__provincia=provincia
            )
            if municipio:
                queryset = queryset.filter(
                    subcategoria__categoria__negocio__municipio=municipio
                )

        return queryset

    def get_paginated_response(self, data):
        assert self.paginator is not None
        
        ordered_params = OrderedDict()
        
        if 'provincia' in self.request.query_params:
            ordered_params['provincia'] = self.request.query_params['provincia']
        
        if 'municipio' in self.request.query_params:
            ordered_params['municipio'] = self.request.query_params['municipio']
        
        next_url = None
        previous_url = None
        
        if self.paginator.get_next_link():
            ordered_params['page'] = str(self.paginator.page.next_page_number())
            next_url = f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(ordered_params)}"
            
        if self.paginator.get_previous_link():
            ordered_params['page'] = str(self.paginator.page.previous_page_number())
            previous_url = f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(ordered_params)}"

        return Response(OrderedDict([
            ('count', self.paginator.page.paginator.count),
            ('next', next_url),
            ('previous', previous_url),
            ('results', data)
        ]))