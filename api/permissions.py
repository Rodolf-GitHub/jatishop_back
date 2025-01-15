from rest_framework import permissions
from .models import NegocioUser

class IsNegocioOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los dueños del negocio
    editar sus propios objetos.
    """
    def has_permission(self, request, view):
        # Permitir GET, HEAD u OPTIONS a cualquiera
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Debe estar autenticado para métodos POST, PUT, DELETE
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permitir GET, HEAD u OPTIONS a cualquiera
        if request.method in permissions.SAFE_METHODS:
            return True

        # Obtener el negocio asociado al objeto
        if hasattr(obj, 'negocio'):
            negocio = obj.negocio
        elif hasattr(obj, 'categoria'):
            negocio = obj.categoria.negocio
        elif hasattr(obj, 'subcategoria'):
            negocio = obj.subcategoria.categoria.negocio
        else:
            return False

        # Verificar si el usuario es dueño del negocio
        try:
            NegocioUser.objects.get(user=request.user, negocio=negocio)
            return True
        except NegocioUser.DoesNotExist:
            return False 