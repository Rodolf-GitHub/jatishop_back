from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from ..models import Licencia, InfoNegocio
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from datetime import timedelta
import logging
import sys

logger = logging.getLogger(__name__)

scheduler = None

def verificar_sistema_licencias():
    """Función que ejecuta todas las verificaciones del sistema de licencias"""
    print("Ejecutando verificación de licencias...")  # Debug print
    try:
        # 1. Verificar licencias vencidas
        licencias_activas = Licencia.objects.filter(esta_activa=True)
        print(f"Verificando {licencias_activas.count()} licencias activas")  # Debug print
        logger.info(f"Iniciando verificación de {licencias_activas.count()} licencias activas")
        
        for licencia in licencias_activas:
            estado_anterior = licencia.esta_activa
            licencia.verificar_estado()
            if estado_anterior != licencia.esta_activa:
                print(f"Cambio de estado en licencia: {licencia.negocio.nombre}")  # Debug print
                logger.info(f"Licencia del negocio {licencia.negocio.nombre} ha cambiado de estado: {estado_anterior} -> {licencia.esta_activa}")

        # 2. Crear licencias para negocios que no tienen
        negocios_sin_licencia = InfoNegocio.objects.filter(licencia__isnull=True)
        for negocio in negocios_sin_licencia:
            fecha_vencimiento = timezone.now() + timedelta(days=30)
            Licencia.objects.create(
                negocio=negocio,
                fecha_vencimiento=fecha_vencimiento,
                tipo_licencia='MENSUAL'
            )
            print(f"Nueva licencia creada para: {negocio.nombre}")  # Debug print
            logger.info(f"Licencia mensual creada para negocio: {negocio.nombre}")

        print("Verificación completada")  # Debug print
        logger.info(f"Verificación completa del sistema de licencias finalizada: {timezone.now()}")
    except Exception as e:
        print(f"Error en verificación: {str(e)}")  # Debug print
        logger.error(f"Error en verificación del sistema de licencias: {str(e)}")

def start_scheduler_if_needed():
    """Función para iniciar el scheduler si no está corriendo"""
    global scheduler
    if not scheduler or not getattr(scheduler, 'running', False):
        print("Iniciando nuevo scheduler...")  # Debug print
        verificar_sistema_licencias()
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            verificar_sistema_licencias,
            'interval',
            minutes=1,
            id='verificar_sistema_licencias_job',
            next_run_time=timezone.now()
        )
        scheduler.start()
        print(f"Nuevo scheduler iniciado y corriendo")  # Debug print
        return True
    return False

@receiver(post_save, sender=InfoNegocio)
def crear_licencia_automatica(sender, instance, created, **kwargs):
    print(f"Signal post_save triggered para {instance.nombre}")  # Debug print
    try:
        if created and not hasattr(instance, 'licencia'):
            fecha_vencimiento = timezone.now() + timedelta(days=30)
            Licencia.objects.create(
                negocio=instance,
                fecha_vencimiento=fecha_vencimiento,
                tipo_licencia='MENSUAL'
            )
            print(f"Licencia creada para nuevo negocio: {instance.nombre}")  # Debug print
            logger.info(f"Licencia mensual creada automáticamente para el nuevo negocio {instance.nombre}")
    except Exception as e:
        print(f"Error en crear_licencia_automatica: {str(e)}")  # Debug print
        logger.error(f"Error al crear licencia automática: {str(e)}")

@receiver(post_migrate)
def configurar_sistema_licencias(sender, **kwargs):
    print("Signal post_migrate triggered")  # Debug print
    try:
        if sender.name == 'api':
            print("Configurando sistema de licencias...")  # Debug print
            start_scheduler_if_needed()
            cache.set('scheduler_started', True)
            print("Sistema de licencias configurado")  # Debug print
            logger.info("Sistema de licencias iniciado después de migración")
    except Exception as e:
        print(f"Error en configurar_sistema_licencias: {str(e)}")  # Debug print
        logger.error(f"Error al configurar sistema de licencias: {str(e)}")

# Inicialización al cargar el módulo
print("Módulo de signals cargado - Iniciando configuración inicial")  # Debug print
start_scheduler_if_needed()