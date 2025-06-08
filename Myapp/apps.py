from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Myapp'

class YourAppConfig(AppConfig):
    name = 'Myapp'

    def ready(self):
        import Myapp.signals  # Replace `your_app` with the actual app name
