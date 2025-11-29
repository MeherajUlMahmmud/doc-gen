from storages.backends.s3boto3 import S3Boto3Storage

from base import settings


class MediaStorage(S3Boto3Storage):
    """Storage class for media files"""
    bucket_name = settings.AWS_BUCKET_NAME
    location = 'media'
    file_overwrite = False
