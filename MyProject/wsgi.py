# """
# WSGI config for MyProject project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyProject.settings')

# application = get_wsgi_application()
# Temporary code to auto-create superuser (remove after 1st deployment)
try:
    from Myapp.create_admin import *
except Exception as e:
    print("Superuser creation skipped:", e)
