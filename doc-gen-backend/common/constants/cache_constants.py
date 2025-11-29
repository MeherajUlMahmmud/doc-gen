# Cache time constants in seconds
CACHE_TIME_SHORT = 60 * 5  # 5 minutes
CACHE_TIME_MEDIUM = 60 * 15  # 15 minutes
CACHE_TIME_LONG = 60 * 60  # 1 hour

# Static file cache constants
CACHE_TIME_STATIC_CSS_JS = 31536000  # 1 year for CSS/JS files
CACHE_TIME_STATIC_IMAGES = 31536000  # 1 year for images
CACHE_TIME_STATIC_FONTS = 31536000  # 1 year for fonts
CACHE_TIME_STATIC_MEDIA = 2592000  # 1 month for media files
CACHE_TIME_STATIC_DOCUMENTS = 604800  # 1 week for documents
CACHE_TIME_STATIC_CONFIG = 86400  # 1 day for config files

# API cache constants
CACHE_TIME_API_PUBLIC = 3600  # 1 hour for public API responses
CACHE_TIME_API_AUTHENTICATED = 300  # 5 minutes for authenticated API responses
CACHE_TIME_API_DYNAMIC = 60  # 1 minute for dynamic content

# Template cache constants
CACHE_TIME_TEMPLATE_STATIC = 3600  # 1 hour for static templates
CACHE_TIME_TEMPLATE_DYNAMIC = 300  # 5 minutes for dynamic templates
