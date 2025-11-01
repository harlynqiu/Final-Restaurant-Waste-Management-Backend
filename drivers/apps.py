from django.apps import AppConfig

class DriversConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drivers'

    def ready(self):
        import drivers.signals  # ✅ this ensures signals are loaded
