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
import os
from termcolor import colored

logger = logging.getLogger(__name__)

scheduler = None

def verificar_sistema_licencias():
    """Función que ejecuta todas las verificaciones del sistema de licencias"""
    try:
        print(colored("\nEjecutando verificación de licencias:", 'cyan', attrs=['bold']))

        # Verificar licencias
        licencias = Licencia.objects.all()
        licencias_activas = [l for l in licencias if l.esta_activa]
        licencias_vencidas = [l for l in licencias if not l.esta_activa]
        
        # Mostrar conteo de licencias
        print(colored(f"✓ Licencias activas ({len(licencias_activas)})", 'green', attrs=['bold']))
        print(colored(f"✗ Licencias vencidas ({len(licencias_vencidas)})", 'red', attrs=['bold']))

        # Crear licencias faltantes
        negocios_sin_licencia = InfoNegocio.objects.filter(licencia__isnull=True)
        if negocios_sin_licencia:
            print(colored(f"+ Creando licencias ({len(negocios_sin_licencia)}):", 'yellow', attrs=['bold']))
            for negocio in negocios_sin_licencia:
                fecha_vencimiento = timezone.now() + timedelta(days=30)
                Licencia.objects.create(
                    negocio=negocio,
                    fecha_vencimiento=fecha_vencimiento
                )
                print(colored(f"  • {negocio.nombre}", 'yellow'))

        print()  # Línea en blanco al final
        logger.info(f"Verificación: {len(licencias_activas)} activas, {len(licencias_vencidas)} vencidas")

    except Exception as e:
        error_msg = f"Error en verificación: {str(e)}"
        print(colored(error_msg, 'red', attrs=['bold']))
        logger.error(error_msg)

def start_scheduler_if_needed():
    """Función para iniciar el scheduler si no está corriendo"""
    global scheduler
    if not scheduler or not getattr(scheduler, 'running', False):
        if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_SETTINGS_MODULE'):
            print(colored("Iniciando scheduler de licencias...", 'cyan', attrs=['bold']))
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
            print(colored("✓ Scheduler iniciado", 'green', attrs=['bold']))
            return True
    return False

@receiver(post_save, sender=InfoNegocio)
def crear_licencia_automatica(sender, instance, created, **kwargs):
    try:
        if created and not hasattr(instance, 'licencia'):
            fecha_vencimiento = timezone.now() + timedelta(days=30)
            Licencia.objects.create(
                negocio=instance,
                fecha_vencimiento=fecha_vencimiento
            )
            print(colored(f"✓ Nueva licencia: {instance.nombre}", 'green'))
            logger.info(f"Licencia creada para {instance.nombre}")
    except Exception as e:
        print(colored(f"✗ Error al crear licencia: {str(e)}", 'red', attrs=['bold']))
        logger.error(f"Error licencia: {str(e)}")

@receiver(post_migrate)
def configurar_sistema_licencias(sender, **kwargs):
    try:
        if sender.name == 'api':
            print(colored("Configurando sistema de licencias...", 'cyan', attrs=['bold']))
            start_scheduler_if_needed()
            cache.set('scheduler_started', True)
            print(colored("✓ Sistema configurado", 'green', attrs=['bold']))
    except Exception as e:
        print(colored(f"✗ Error de configuración: {str(e)}", 'red', attrs=['bold']))
        logger.error(f"Error config: {str(e)}")

# Inicialización
print(colored("Iniciando sistema de licencias...", 'cyan', attrs=['bold']))
start_scheduler_if_needed()