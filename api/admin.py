from django.contrib import admin
from django.apps import apps
from .models import *
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect

@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'fecha_vencimiento', 'esta_activa', 'dias_restantes']
    list_filter = ['esta_activa']
    search_fields = ['negocio__nombre']
    readonly_fields = ['fecha_inicio']
    
    def response_change(self, request, obj):
        if "_extender_un_mes" in request.POST:
            self._extender_licencia(obj, 30)
            self.message_user(request, "Se extendió la licencia por 1 mes", messages.SUCCESS)
            return redirect('admin:api_licencia_change', obj.pk)
        
        if "_extender_tres_meses" in request.POST:
            self._extender_licencia(obj, 90)
            self.message_user(request, "Se extendió la licencia por 3 meses", messages.SUCCESS)
            return redirect('admin:api_licencia_change', obj.pk)
            
        if "_extender_seis_meses" in request.POST:
            self._extender_licencia(obj, 180)
            self.message_user(request, "Se extendió la licencia por 6 meses", messages.SUCCESS)
            return redirect('admin:api_licencia_change', obj.pk)
            
        if "_extender_un_año" in request.POST:
            self._extender_licencia(obj, 365)
            self.message_user(request, "Se extendió la licencia por 1 año", messages.SUCCESS)
            return redirect('admin:api_licencia_change', obj.pk)
            
        if "_vencer_licencia" in request.POST:
            self._vencer_licencia(obj)
            self.message_user(request, "La licencia ha sido vencida y el negocio desactivado", messages.WARNING)
            return redirect('admin:api_licencia_change', obj.pk)
            
        return super().response_change(request, obj)

    def _extender_licencia(self, licencia, dias):
        if licencia.fecha_vencimiento < timezone.now():
            licencia.fecha_vencimiento = timezone.now() + timedelta(days=dias)
        else:
            licencia.fecha_vencimiento += timedelta(days=dias)
        licencia.esta_activa = True
        licencia.negocio.activo = True
        licencia.negocio.save()
        licencia.save()

    def _vencer_licencia(self, licencia):
        # Establecer la fecha de vencimiento un segundo antes de la fecha actual
        licencia.fecha_vencimiento = timezone.now() - timedelta(seconds=1)
        licencia.esta_activa = False
        licencia.negocio.activo = False
        licencia.negocio.save()
        licencia.save()

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/extender-un-mes/',
                self.admin_site.admin_view(self.extender_un_mes_view),
                name='licencia-extender-un-mes',
            ),
            path(
                '<path:object_id>/extender-tres-meses/',
                self.admin_site.admin_view(self.extender_tres_meses_view),
                name='licencia-extender-tres-meses',
            ),
            path(
                '<path:object_id>/extender-seis-meses/',
                self.admin_site.admin_view(self.extender_seis_meses_view),
                name='licencia-extender-seis-meses',
            ),
            path(
                '<path:object_id>/extender-un-año/',
                self.admin_site.admin_view(self.extender_un_año_view),
                name='licencia-extender-un-año',
            ),
        ]
        return custom_urls + urls

    def extender_un_mes_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        self._extender_licencia(obj, 30)
        self.message_user(request, "Se extendió la licencia por 1 mes", messages.SUCCESS)
        return redirect('admin:api_licencia_change', object_id)

    def extender_tres_meses_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        self._extender_licencia(obj, 90)
        self.message_user(request, "Se extendió la licencia por 3 meses", messages.SUCCESS)
        return redirect('admin:api_licencia_change', object_id)

    def extender_seis_meses_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        self._extender_licencia(obj, 180)
        self.message_user(request, "Se extendió la licencia por 6 meses", messages.SUCCESS)
        return redirect('admin:api_licencia_change', object_id)

    def extender_un_año_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        self._extender_licencia(obj, 365)
        self.message_user(request, "Se extendió la licencia por 1 año", messages.SUCCESS)
        return redirect('admin:api_licencia_change', object_id)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'show_save_and_continue': False,
            'show_save': True,
        })
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

# Registrar automáticamente el resto de los modelos
app_models = apps.get_app_config('api').get_models()
for model in app_models:
    if model not in [Licencia]:
        admin.site.register(model)