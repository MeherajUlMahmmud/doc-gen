from django.urls import path

from common.views.common import IndexView, ping
from common.views.log import LogAPIView

urlpatterns = [
    # API endpoints
    path('api-index/', IndexView.as_view(), name='api_index'),
    path('api/', IndexView.as_view()),
    path('ping/', ping),

    path('api/logs/', LogAPIView.as_view(), name='log-api'),
    # path('api/celery-logs/', CeleryLogStreamView.as_view(), name='celery_logs'),
    # path('api/celery-control/', CeleryControlView.as_view(), name='celery_control'),

    # Contact Us endpoints (TODO: implement these views)
    # path('api/contact-us/create/', ContactUsCreateAPIView.as_view(), name='contact_us'),
    # path('api/contact-us/list/', ContactUsListAPIView.as_view(), name='contact_us_list'),
    # path('api/contact-us/<str:pk>/details/', ContactUsDetailAPIView.as_view(), name='contact_us_detail'),
    # path('api/contact-us/<str:pk>/delete/', ContactUsDeleteAPIView.as_view(), name='contact_us_delete'),
]
