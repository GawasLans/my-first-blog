import os
import sys

# Agrega la ruta de la carpeta de tu proyecto al path de Python.
path = '/home/gastón/Nueva carpeta/teamheroes/'  # Asegúrate de que esta es la ruta correcta
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Esta es la configuración clave para servir archivos estáticos y tu aplicación.
application = StaticFilesHandler(get_wsgi_application())
