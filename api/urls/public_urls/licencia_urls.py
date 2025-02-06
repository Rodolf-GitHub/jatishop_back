from django.urls import path
from ...views.public_views.licence_view import LicenciaEstadoView

urlpatterns = [
    path('estado/', LicenciaEstadoView.as_view(), name='licencia-estado'),
]