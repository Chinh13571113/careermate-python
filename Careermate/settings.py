from pathlib import Path
import os
import warnings
from dotenv import load_dotenv

# Suppress Triton warnings about missing CUDA binaries (for CPU-only PyTorch usage)
warnings.filterwarnings('ignore', message='Failed to find.*', module='triton.knobs')

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SPRING_BOOT_JWT_SECRET = os.environ["SPRING_BOOT_JWT_SECRET"]

SECRET_KEY = 'django-insecure-your-secret-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',  # Add CORS headers support
    # Add your app
    'apps.roadmap_agent',
    'apps.recommendation_agent',
    'apps.cv_creation_agent',
    'apps.cv_analysis_agent',
    'apps.swagger.apps.SwaggerConfig',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.swagger.authentication.BearerAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require authentication by default
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Careermate API',
    'DESCRIPTION': 'API documentation with Swagger UI',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'bearerAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add CORS middleware here (before CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Careermate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Careermate.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'MyPostgresDB'),
        'USER': os.environ.get('POSTGRES_USER', 'root'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '123456'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5439'),
    },
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = os.environ["CELERY_TASK_TIME_LIMIT"]  # 30 minutes
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
    "http://localhost:4200",  # Angular default port
    "http://localhost:8080",  # Vue default port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:8080",
]

# Allow credentials (cookies, authorization headers, etc.)
CORS_ALLOW_CREDENTIALS = True

# Allow all headers and methods for development
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# For production, you should also update ALLOWED_HOSTS
# ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
