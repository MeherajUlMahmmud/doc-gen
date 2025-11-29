from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin-VPzUF4v/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    # API endpoints (must come before template views to take precedence)
    path("", include("document_control.urls")),
    path("", include("user_control.urls")),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
