import datetime
import os
from pathlib import Path

from celery.schedules import crontab
from decouple import config
import dj_database_url

from base.log_filters import ExcludePatternFilter, TraceIDFilter, RelativePathFilter

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

os.makedirs(os.path.join(BASE_DIR, 'logs/debug'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'logs/app'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'logs/celery'), exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default='True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

MAX_UPLOAD_SIZE = 5242880  # 5MB

FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
SERVER_URL = config('SERVER_URL', default='http://localhost:8000')

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')
GOOGLE_MAPS_AUTOCOMPLETE_COUNTRIES = [
    code.strip().lower()
    for code in config('GOOGLE_MAPS_AUTOCOMPLETE_COUNTRIES', default='au').split(',')
    if code.strip()
]

# Application definition
INSTALLED_APPS = [
    # Custom apps
    'common.apps.CommonConfig',
    'user_control.apps.UserControlConfig',
    'document_control.apps.DocumentControlConfig',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    "django_filters",
    "jazzmin",
    'corsheaders',
    'import_export',
    'rest_framework_swagger',  # Swagger
    'drf_yasg',  # Yet Another Swagger generator
    'django_extensions',

    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    'base.middleware.CacheRequestBodyMiddleware',
    'corsheaders.middleware.CorsMiddleware',

    # Django built-in middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Custom middleware (should come after Django's built-in middleware)
    'base.middleware.CacheControlMiddleware',
    'base.middleware.TraceIDMiddleware',
    'base.middleware.RequestLogMiddleware',
    'base.middleware.IPBlockerMiddleware',
    'base.middleware.IPTrackingMiddleware',
    'base.middleware.XRobotsTagMiddleware',
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "base.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Use dj-database-url to parse the DATABASE_URL environment variable
DATABASE_URL = config('DEV_DATABASE_URL', default='sqlite:///db.sqlite3') if DEBUG else config('PROD_DATABASE_URL',
                                                                                               default='sqlite:///db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Cache settings
# Use Redis for caching (database 1, while Celery uses database 0)
CACHE_URL = config('CACHE_URL', default='redis://localhost:6379/1')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,  # seconds
            'SOCKET_TIMEOUT': 5,  # seconds
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Fail silently if Redis is unavailable
        },
        'KEY_PREFIX': 'shining_services',
        'TIMEOUT': 300,  # Default timeout in seconds (5 minutes)
    }
}

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / "static"]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "user_control.UserModel"

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Storage configuration
STORAGE_TYPE = config('STORAGE_TYPE', default='local')

# API

# Configure Django Rest Framework
REST_FRAMEWORK = {
    'NON_FIELD_ERRORS_KEY': 'error',
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'user_control.authentication.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DATETIME_INPUT_FORMATS': ['%Y-%m-%d %H:%M', '%Y-%m-%d'],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
}

# Configure Django Rest Framework Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=28),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Configure Django Rest Framework Swagger
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Configure Django CORS Headers
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
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
CORS_EXPOSE_HEADERS = [
    'content-disposition',
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Security

# Security settings
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'ALLOW'

# Get the real IP address from proxy headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Session settings
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds

# IP blocking settings
IP_BLOCK_MAX_ATTEMPTS = int(config("IP_BLOCK_MAX_ATTEMPTS", default=3))
IP_WHITELIST = config('IP_WHITELIST', default='127.0.0.1,').split(',')

# Sensitive patterns for IP blocking
IP_BLOCK_PATTERNS = [
    # Original patterns
    r'\.env',
    r'\.git',
    r'\.htaccess',
    r'wp-config\.php',
    r'config\.php',
    r'\.sql',
    r'\.bak',
    r'\.old',
    r'\.backup',
    r'\.swp',
    r'\.config',
    r'geoserver',
    r'nginx',
    r'webui',
    r's3',
    r'configs',
    r'k8s',
    r'subdomains',

    # Config and credential files
    r'\.aws',
    r'aws[-_]config',
    r'aws[-_]credentials',
    r'credentials\.(json|yml|yaml|xml|ini|csv)',
    r'config\.(js|json|yml|yaml|xml|ini|env|php|conf|toml)',
    r'\.circleci',
    r'\.github/workflows',
    r'\.gitlab-ci',
    r'\.terraformrc',
    r'\.tfvars',
    r'terraform',
    r'secrets\.',
    r'parameters\.(yml|yaml|xml|json|ini)',
    r'sendgrid[-_]keys',
    r'\.kube/config',
    r'\.env\.',
    r'\.env[-_]',
    r'env\..*',
    r'\.production',
    r'\.dockerenv',

    # Database and admin access
    r'phpmyadmin',
    r'php.*info',
    r'info\.php',
    r'db(admin|web|manager)',
    r'mysql(admin|manager)',
    r'adminer\.php',
    r'sqladmin',
    r'wp-admin',
    r'administrator',
    r'admin\.php',

    # System/file access attempts
    r'\.ssh',
    r'\.vscode',
    r'_profiler',
    r'\.svn',
    r'\.idea',
    r'\.DS_Store',
    r'actuator',
    r'solr/admin',
    r'jenkins',
    r'hudson',
    r'console',
    r'wp-content',
    r'wp-includes',

    # API and web vulnerabilities
    r'cgi-bin',
    r'owa/auth',
    r'dana-na',
    r'boaform',
    r'HNAP1',
    r'phpunit',
    r'eval-stdin\.php',
    r'api/sonicos',
    r'Autodiscover',
    r'wp-json',
    r'rest/applinks',
    r'confluence/rest',
    r'Telerik\.Web\.UI',
    r'vendor/phpunit',
    r'ckeditor',
    r'portal/redlion',
    r'nmaplowercheck',
    r'logincheck',

    # Cloud metadata access attempts
    r'latest/meta-data',
    r'169\.254\.169\.254',

    # WebShells/Backdoors
    r'(sh|up|tz|token|time|test.*|temp|old_phpinfo|lindex|jo|inf|in|i)\.php$',

    # Server Status and Diagnostics
    r'server[-_]status',
    r'status\.php',
    r'server[-_]info',

    # Docker/Kubernetes
    r'docker[-_]',
    r'containers/json',
    r'pools/default/buckets',

    # Authentication endpoints
    r'login\.(php|jsp|do|action|htm|html|aspx|cc)',
    r'logon\.',
    r'auth\.',
    r'j_spring_security_check',
    r'identity',
]

# Logging

# Request logging settings
REQUEST_LOG_EXCLUDED_PATHS = [
    r'^/admin',
    r'^/favicon\.ico',
    r'^/static',
    r'^/media',
]
REQUEST_LOG_MAX_CONTENT_SIZE = int(
    config('REQUEST_LOG_MAX_CONTENT_SIZE', default=10000))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_pattern_filter': {
            '()': ExcludePatternFilter,
        },
        'trace_id_filter': {
            '()': TraceIDFilter,
        },
        'relative_path_filter': {
            '()': RelativePathFilter,
        }
    },
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} {trace_id} {relative_path}:{lineno} {module} {message}',
            'style': '{',
        },
        'celery': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'filters': [
                'exclude_pattern_filter',
                'trace_id_filter',
                'relative_path_filter'
            ],
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/debug/debug.log'),
            'formatter': 'standard',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
        },
        'app_file': {
            'level': 'INFO',
            'filters': [
                'exclude_pattern_filter',
                'trace_id_filter',
                'relative_path_filter'
            ],
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/app/app.log'),
            'formatter': 'standard',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': [
                'trace_id_filter',
                'relative_path_filter'
            ],
            'formatter': 'standard',
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/celery/celery.log'),
            'formatter': 'celery',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.worker': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.beat': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'debug': {
            'handlers': ['debug_file', 'app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {  # Root logger
            'handlers': ['app_file', 'console'],
            'level': 'DEBUG',
        },
    }
}

# Third Party

# Configure Django Jazzmin
JAZZMIN_SETTINGS = {
    # Site information
    'site_title': 'Shining Services',
    'site_header': 'Shining Services Admin',
    'site_brand': 'Shining Services',
    'site_logo_classes': 'img-circle',
    'site_icon': "assets/logo.png",
    'welcome_sign': 'Welcome to Shining Services Admin Portal',
    'copyright': 'Shining Services',
    'site_url': 'https://www.shiningservices.com.au',

    # User interface
    'search_model': [],
    'user_avatar': None,
    'show_ui_builder': True,
    'navigation_expanded': True,
    'show_sidebar': True,
    'sidebar_fixed': True,
    'related_modal_active': True,
    'show_full_screen': True,
    'show_drug_title': True,
    'drug_title': 'Shining Services',

    # Theme settings
    'theme': 'flatly',
    'dark_mode_theme': 'darkly',
    'icon_theme': 'fontawesome',
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success'
    },

    # Top menu configuration
    'topmenu_links': [
        {
            'name': 'Dashboard',
            'url': 'admin:index',
            'permissions': ['auth.view_user']
        },
        {'app': 'common'},
        {'app': 'portal'},
        {'app': 'user_control'},
        {'app': 'service_control'},
        {'app': 'order_control'},
    ],

    # Side menu configuration
    'order_with_respect_to': [
        'common',
        'portal',
        'user_control',
        'order_control',
        'job_control',
        'service_control',
    ],
    'hide_apps': [],
    'hide_models': [],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'user_control.UserModel': 'fas fa-user-shield',
        'user_control.LoginAttemptModel': 'fas fa-sign-in-alt',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-file',

    # Form appearance
    'changeform_format': 'horizontal_tabs',
    # 'changeform_format_overrides': {
    #     'user_control.UserModel': 'collapsible',
    #     'auth.user': 'vertical_tabs',
    # },

    # Form actions
    'actions_sticky_top': True,
}

# Configure Django Import Export
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = 'change'
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'
IMPORT_EXPORT_RESOURCE_CLASS = 'import_export.resources.ModelResource'
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.TempFolderStorage'

# Configure WhiteNoise for static files
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG

# WhiteNoise cache configuration for efficient static file serving
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0  # 1 year in production, no cache in debug
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_ADD_HEADERS_FUNCTION = 'base.staticfiles.add_cache_headers'

# Celery settings (if using Celery)
CELERY_BROKER_URL = config(
    'CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_TASK_EAGER_PROPAGATES = DEBUG

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
    ]
    INTERNAL_IPS = ['127.0.0.1']
    # REST_FRAMEWORK = {
    #     'DEFAULT_RENDERER_CLASSES': [
    #         'rest_framework.renderers.JSONRenderer',
    #         'rest_framework.renderers.BrowsableAPIRenderer',
    #     ]
    # }
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
