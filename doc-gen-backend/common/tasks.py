import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from common.models import RequestLog

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BATCH_SIZE = 10


@shared_task
def delete_old_request_logs():
    """
    Celery task to delete request logs older than 2 months
    """
    two_months_ago = timezone.now() - timedelta(days=60)

    # Delete logs older than 2 months
    deleted_count, _ = RequestLog.objects.filter(
        created_at__lt=two_months_ago).delete()

    logger.info(f'Deleted {deleted_count} old request logs')

# @shared_task
# def send_push_notification_task(notification_type: str, title: str, body: str, 
#                               target_type: str = 'admin', user_id: str = None,
#                               data: dict = None, priority: str = 'normal'):
#     """
#     Celery task to send push notifications asynchronously.

#     Args:
#         notification_type: Type of notification (e.g., 'quote_created', 'order_status_changed')
#         title: Notification title
#         body: Notification body
#         target_type: Who to send to ('admin', 'user', 'all')
#         user_id: User ID if target_type is 'user'
#         data: Additional data to send with notification
#         priority: Notification priority ('normal' or 'high')
#     """
#     try:
#         from .notification_service import notification_service

#         logger.info(f'[send_push_notification_task] Starting notification task: {notification_type}')

#         if target_type == 'admin':
#             result = notification_service.send_notification_to_admin_devices(
#                 title=title, body=body, data=data, priority=priority
#             )
#         elif target_type == 'user' and user_id:
#             result = notification_service.send_notification_to_user(
#                 user_id=user_id, title=title, body=body, data=data, priority=priority
#             )
#         elif target_type == 'all':
#             result = notification_service.send_notification_to_all_devices(
#                 title=title, body=body, data=data, priority=priority
#             )
#         else:
#             logger.error(f'[send_push_notification_task] Invalid target_type: {target_type}')
#             return

#         logger.info(f'[send_push_notification_task] Notification sent successfully. Result: {result}')

#     except Exception as e:
#         logger.error(f'[send_push_notification_task] Failed to send notification: {str(e)}', exc_info=True)


# @shared_task
# def process_notification_queue():
#     """
#     Celery task to process and send pending notifications from NotificationQueueModel.
#     Runs every 2 minutes (should be scheduled via Celery beat).
#     """
#     try:
#         from .notification_queue_service import NotificationQueueService

#         logger.info('[process_notification_queue] Starting notification queue processing')

#         # Process notifications in batches
#         result = NotificationQueueService.process_notification_queue(batch_size=20)

#         logger.info(f'[process_notification_queue] Queue processing completed. Result: {result}')

#         return result

#     except Exception as e:
#         logger.error(f'[process_notification_queue] Failed to process notification queue: {str(e)}', exc_info=True)
#         return {'error': str(e)}


# @shared_task
# def retry_failed_notifications():
#     """
#     Celery task to retry failed notifications that haven't exceeded max retries.
#     Runs every 10 minutes (should be scheduled via Celery beat).
#     """
#     try:
#         from .notification_queue_service import NotificationQueueService

#         logger.info('[retry_failed_notifications] Starting retry of failed notifications')

#         # Retry failed notifications
#         result = NotificationQueueService.retry_failed_notifications(batch_size=30)

#         logger.info(f'[retry_failed_notifications] Retry processing completed. Result: {result}')

#         return result

#     except Exception as e:
#         logger.error(f'[retry_failed_notifications] Failed to retry failed notifications: {str(e)}', exc_info=True)
#         return {'error': str(e)}


# @shared_task
# def cleanup_expired_notifications():
#     """
#     Celery task to clean up expired notifications from the queue.
#     Runs every hour (should be scheduled via Celery beat).
#     """
#     try:
#         from .notification_queue_service import NotificationQueueService

#         logger.info('[cleanup_expired_notifications] Starting cleanup of expired notifications')

#         # Clean up expired notifications
#         cleaned_count = NotificationQueueService.cleanup_expired_notifications()

#         if cleaned_count > 0:
#             logger.info(f'[cleanup_expired_notifications] Cleaned up {cleaned_count} expired notifications')
#         else:
#             logger.info('[cleanup_expired_notifications] No expired notifications to clean up')

#         return {'cleaned_count': cleaned_count}

#     except Exception as e:
#         logger.error(f'[cleanup_expired_notifications] Failed to cleanup expired notifications: {str(e)}', exc_info=True)
#         return {'error': str(e)}


# @shared_task
# def queue_notification_task(
#     title: str,
#     body: str,
#     target_type: str = 'admin',
#     user_id: str = None,
#     data: dict = None,
#     priority: str = 'normal',
#     priority_level: int = 1,
#     notification_type: str = None,
#     source_app: str = None,
#     scheduled_at: str = None,
#     expires_at: str = None,
#     batch_id: str = None
# ):
#     """
#     Celery task to queue a notification for asynchronous processing.

#     Args:
#         title: Notification title
#         body: Notification body
#         target_type: Type of target ('admin', 'user', 'all', 'custom')
#         user_id: User ID if target_type is 'user'
#         data: Additional data payload
#         priority: Notification priority ('normal' or 'high')
#         priority_level: Queue processing priority (0-3)
#         notification_type: Type/category of notification
#         source_app: Source application name
#         scheduled_at: ISO string for scheduled sending time
#         expires_at: ISO string for expiration time
#         batch_id: Batch ID for grouping
#     """
#     try:
#         from .notification_queue_service import NotificationQueueService
#         from django.utils.dateparse import parse_datetime

#         logger.info(f'[queue_notification_task] Queuing notification: {title}')

#         # Parse datetime strings if provided
#         scheduled_datetime = None
#         expires_datetime = None

#         if scheduled_at:
#             scheduled_datetime = parse_datetime(scheduled_at)
#         if expires_at:
#             expires_datetime = parse_datetime(expires_at)

#         # Queue the notification
#         notification = NotificationQueueService.queue_notification(
#             title=title,
#             body=body,
#             target_type=target_type,
#             user_id=user_id,
#             data=data,
#             priority=priority,
#             priority_level=priority_level,
#             notification_type=notification_type,
#             source_app=source_app,
#             scheduled_at=scheduled_datetime,
#             expires_at=expires_datetime,
#             batch_id=batch_id
#         )

#         logger.info(f'[queue_notification_task] Notification queued successfully. ID: {notification.id}')

#         return {
#             'success': True,
#             'notification_id': str(notification.id),
#             'status': notification.status
#         }

#     except Exception as e:
#         logger.error(f'[queue_notification_task] Failed to queue notification: {str(e)}', exc_info=True)
#         return {'success': False, 'error': str(e)}
