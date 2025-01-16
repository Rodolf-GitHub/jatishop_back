from rest_framework import permissions
from .models import NegocioUser, InfoNegocio

class IsNegocioOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los dueños del negocio
    realizar operaciones de escritura.
    """
    def has_permission(self, request, view):
        # Permitir GET, HEAD u OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Verificar si el usuario está autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # Obtener el slug del negocio de la URL
        negocio_slug = view.kwargs.get('negocio_slug')
        if not negocio_slug:
            return False

        try:
            # Verificar si el usuario es dueño del negocio
            negocio = InfoNegocio.objects.get(slug=negocio_slug)
            return NegocioUser.objects.filter(
                user=request.user,
                negocio=negocio
            ).exists()
        except InfoNegocio.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Permitir GET, HEAD u OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Para objetos específicos, verificar si el usuario es dueño del negocio
        try:
            if hasattr(obj, 'negocio'):
                negocio = obj.negocio
            elif hasattr(obj, 'categoria'):
                negocio = obj.categoria.negocio
            elif hasattr(obj, 'subcategoria'):
                negocio = obj.subcategoria.categoria.negocio
            else:
                return False

            return NegocioUser.objects.filter(
                user=request.user,
                negocio=negocio
            ).exists()
        except:
            return False 