
import os
from pathlib import Path
from celery import Celery

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpiedelvolcan_.settings')

# app = Celery('Tours')
# app.config_from_object('django.conf:settings', namespace='CELERY')

#####################################################################################################################
######### configuraciones para celery ###############################################################################
#####################################################################################################################

# Configuración de Azure Service Bus como backend de mensajería
# app.conf.broker_url = 'azureservicebus://volcanocelery.servicebus.windows.net/?operation_timeout=60&'
# app.conf.broker_transport_options = {
#     'polling_interval': 1,
#     'max_retries': 3,
#     'interval_start': 0,
# }
# app.autodiscover_tasks()


# CELERY_BEAT_SCHEDULE = {
#     'actualizar-estado-reserva': {
#         'task': 'Tours.tasks.actualizar_estado_reserva',
#         'schedule': 5.0,  # Ejecutar cada 10 segundos
#     },
# }

#####################################################################################################################
######### configuraciones para celery #################################################################
#####################################################################################################################

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-71ilsry+%0yrbexaf^j!f41b0i=t!g+8%pvd!1d8a)azph_nd-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['volcano-sm.azurewebsites.net', 'http://0.0.0.0:8000/', '127.0.0.1', 'volcanosm.net', '51.222.136.8:8000', '51.222.136.8']
#CORS_ALLOWED_ORIGINS = ['https://alpiedelvolcan.azurewebsites.net/']

# Security & HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://volcano-sm.azurewebsites.net', 'https://volcanosm.net', '51.222.136.8:8000', '51.222.136.8']

#WOMPI CONECTION
CLIENT_ID = "86d5de4c-dd6a-42d2-8d5b-ff5aed09ae83"
CLIENT_SECRET = "c3bb69e4-7d19-486b-b9d8-1b2b592714d5"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # El puerto para Gmail es 587
EMAIL_USE_TLS = True  # Utiliza TLS (Transport Layer Security) para la conexión
EMAIL_HOST_USER = 'volcanosm_reservations@fe12acb8-21f7-46d8-9613-2c3e2746e6a6.azurecomm.net'
EMAIL_HOST_PASSWORD = '18032022#sm'
DEFAULT_FROM_EMAIL = 'volcanosanmiguel.sv@gmail.com'

CKEDITOR_UPLOAD_PATH = "uploads/"

# Application definition

INSTALLED_APPS = [
    # 'material',
    # 'material.admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'Tours',
    'Servicios',
    'Configuraciones',
    'Nosotros',
    'Contactanos',
    'Transacciones',
    'ckeditor',
    'ckeditor_uploader',
    'Utilidades',
    'TPV_.Cajas',
    'TPV_.Clientes',
    'TPV_.Contabilidad',
    'TPV_.Facturas',
    'TPV_.Inventario',
    'TPV_.Kardex',
    'TPV_.Productos',
    'TPV_.Proveedores',
    'TPV_.Ventas',
    'TPV_.Reportes',
    'django_celery_beat',
    'Internet',
    
]

LOGIN_REDIRECT_URL = 'utilidades:utilidades'
LOGOUT_REDIRECT_URL = 'login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alpiedelvolcan_.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/sections'),
            os.path.join(BASE_DIR, 'Tours/templates'),
            os.path.join(BASE_DIR, 'Servicios/templates'),
            os.path.join(BASE_DIR, 'Nosotros/templates'),
            os.path.join(BASE_DIR, 'Contactanos/templates'),
            os.path.join(BASE_DIR, 'Configuraciones/templates'),
            os.path.join(BASE_DIR, 'Transacciones/templates'),
            os.path.join(BASE_DIR, 'Utilidades/templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'TPV_.Ventas.context_processors.categorias_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'alpiedelvolcan_.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cuadmesv_tour',
        'USER': 'cuadmesv_tour',
        'PASSWORD': '8LC*do.&7Emh',
        'HOST': 'www.metrocuadrado.com.sv',
        'PORT': '3306',  # Puerto predeterminado de MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# DATABASES = {
#     'sqlite': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     },
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'cuadmesv_tour_dev',
#         'USER': 'cuadmesv_tour_dev',
#         'PASSWORD': 'Volcano2024$',
#         'HOST': 'www.metrocuadrado.com.sv',
#         'PORT': '3306',  # Puerto predeterminado de MySQL
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }


#AZURE STORE CONFIG
# settings.py
AZURE_ACCOUNT_NAME = 'storagevolcanosm'
AZURE_ACCOUNT_KEY = 'bM1FfTO84g+fuxlgzL87NJiMQYFsZYnBX0KE9rXLfb/oMDQP9J7FToiBjYqIe0qkoMkFti683sC5+AStrLow7w=='
AZURE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagevolcanosm;AccountKey=bM1FfTO84g+fuxlgzL87NJiMQYFsZYnBX0KE9rXLfb/oMDQP9J7FToiBjYqIe0qkoMkFti683sC5+AStrLow7w==;EndpointSuffix=core.windows.net'
AZURE_CONTAINER_NAME = 'imagenes'
AZURE_ENDPOINT_SUFFIX = 'core.windows.net'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# Configuración regional para El Salvador
LANGUAGE_CODE = 'es-SV'
TIME_ZONE = 'America/El_Salvador'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Configuración para archivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = '/static/'

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'


# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
