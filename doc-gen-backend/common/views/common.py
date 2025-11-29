import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


@require_http_methods(["GET"])
def ping(request):
    return HttpResponse("PONG", content_type="text/plain")
