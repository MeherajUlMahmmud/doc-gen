import os

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from base import settings
from common.utils import Utils


# Configure logging
# logger = logging.getLogger('celery_log_stream')
# logger.setLevel(logging.INFO)


class LogAPIView(APIView):
    """
    API view to retrieve and filter application logs.
    Only accessible by admin users.
    """
    permission_classes = [IsAdminUser]
    LOG_LINES_PER_PAGE = 200

    def get(self, request, *args, **kwargs):
        query_params = request.GET
        level = query_params.get('level', '')
        trace_id = query_params.get('trace_id', '')
        logs_per_page = int(query_params.get(
            'logs_per_page', self.LOG_LINES_PER_PAGE))
        page = int(query_params.get('page', 1))
        print(query_params)
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'debug.log')

        start_line = (page - 1) * logs_per_page
        end_line = page * logs_per_page
        print(start_line, end_line, trace_id, level)

        log_lines = Utils.read_log_file(log_file_path, end_line, trace_id, level)

        # Paginate log lines
        paginated_logs = log_lines[start_line:end_line]

        return JsonResponse({
            'logs': paginated_logs,
            'page': page,
            'total_pages': len(log_lines) // self.LOG_LINES_PER_PAGE + 1
        }, safe=False)

#
# class CeleryLogStreamView(APIView):
#     def get(self, request):
#         """
#         Stream Celery logs via Server-Sent Events (SSE)
#         """
#
#         def event_stream():
#             # Open the log file in binary read mode
#             with open(CELERY_LOG_PATH, 'rb') as logfile:
#                 # Seek to the end of the file initially
#                 logfile.seek(0, os.SEEK_END)
#
#                 while True:
#                     # Read new lines
#                     line = logfile.readline()
#                     if not line:
#                         # No new data, wait a bit
#                         time.sleep(0.1)
#                         continue
#
#                     # Decode and yield the line
#                     try:
#                         decoded_line = line.decode('utf-8').strip()
#                         yield f"data: {json.dumps({'log': decoded_line})}\n\n"
#                     except UnicodeDecodeError:
#                         # Handle potential encoding issues
#                         continue
#
#         response = StreamingHttpResponse(
#             event_stream(),
#             content_type='text/event-stream'
#         )
#         response['Cache-Control'] = 'no-cache'
#         response['X-Accel-Buffering'] = 'no'
#         return response
#
#
# class CeleryControlView(APIView):
#     def post(self, request):
#         """
#         Control Celery worker
#         Actions: start, stop, restart
#         """
#         action = request.data.get('action')
#
#         try:
#             if action == 'start':
#                 os.system('celery -A your_project multi start worker1')
#                 return Response({'status': 'Worker started'}, status=status.HTTP_200_OK)
#
#             elif action == 'stop':
#                 os.system('celery -A your_project multi stop worker1')
#                 return Response({'status': 'Worker stopped'}, status=status.HTTP_200_OK)
#
#             elif action == 'restart':
#                 os.system('celery -A your_project multi restart worker1')
#                 return Response({'status': 'Worker restarted'}, status=status.HTTP_200_OK)
#
#             else:
#                 return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
