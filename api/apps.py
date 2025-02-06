from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        try:
            from . import signals  # importamos el módulo completo
            signals.licencia_signals.start_scheduler_if_needed()
            print("Signals cargadas correctamente")  # Debug print
        except Exception as e:
            print(f"Error al cargar signals: {e}")  # Debug print
