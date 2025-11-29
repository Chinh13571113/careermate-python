import os
import warnings
from django.core.wsgi import get_wsgi_application

# Suppress Triton warnings about missing CUDA binaries
warnings.filterwarnings('ignore', message='Failed to find.*', module='triton.knobs')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
application = get_wsgi_application()
