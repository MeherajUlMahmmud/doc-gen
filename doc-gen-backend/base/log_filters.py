import logging
import os
import re
import uuid
from functools import lru_cache
from threading import local
from typing import Optional, List

from django.conf import settings

# Thread-local storage for trace IDs
_local = local()


class ExcludePatternFilter(logging.Filter):
    """
    Filter that excludes log messages matching specific patterns.
    More versatile than the original ExcludeStatReloaderFilter.
    """

    def __init__(self, name: str = '', patterns: Optional[List[str]] = None):
        super().__init__(name)
        self.patterns = []
        if patterns:
            self.add_patterns(patterns)
        else:
            # Default patterns to exclude
            self.add_patterns([
                'Watching for file changes with StatReloader',
                'GET /admin-VPzUF4v',
                'POST /admin-VPzUF4v',
                'PUT /admin-VPzUF4v',
                'PATCH /admin-VPzUF4v',
                'DELETE /admin-VPzUF4v',
                'GET /static/',
                'GET /favicon.ico',
                'reloading',
            ])

    def add_patterns(self, patterns: List[str]) -> None:
        """Add patterns to the exclusion list"""
        for pattern in patterns:
            self.patterns.append(re.compile(re.escape(pattern)))

    def add_regex_patterns(self, patterns: List[str]) -> None:
        """Add regex patterns to the exclusion list without escaping"""
        for pattern in patterns:
            self.patterns.append(re.compile(pattern))

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern in self.patterns:
            if pattern.search(message):
                return False
        return True


class TraceIDFilter(logging.Filter):
    """
    Adds a trace ID to log records for request tracking.
    """

    def __init__(self, name: str = '', trace_id_attr: str = 'trace_id'):
        super().__init__(name)
        self.trace_id_attr = trace_id_attr

    def filter(self, record: logging.LogRecord) -> bool:
        trace_id = getattr(_local, 'trace_id', None)
        if not trace_id:
            trace_id = uuid.uuid4().hex
            _local.trace_id = trace_id

        setattr(record, self.trace_id_attr, trace_id)
        return True


class RelativePathFilter(logging.Filter):
    """
    Adds a relative path attribute to log records.
    """

    def __init__(self, name: str = '', max_path_length: int = 50,
                 path_attr: str = 'relative_path', base_dir: Optional[str] = None):
        super().__init__(name)
        self.max_path_length = max_path_length
        self.path_attr = path_attr
        self.base_dir = base_dir or getattr(settings, 'BASE_DIR', None)

    def filter(self, record: logging.LogRecord) -> bool:
        # Get relative path
        relative_path = self.get_relative_path(record.pathname)

        # Truncate long paths if needed
        if len(relative_path) > self.max_path_length:
            relative_path = '...' + relative_path[-self.max_path_length:]

        setattr(record, self.path_attr, relative_path)
        return True

    def get_relative_path(self, absolute_path: str) -> str:
        """Get path relative to base directory"""
        if not self.base_dir:
            return absolute_path

        try:
            return os.path.relpath(absolute_path, self.base_dir)
        except ValueError:
            return absolute_path


class LogLevelFilter(logging.Filter):
    """
    Filter that only allows records with a specific log level or range of levels.
    """

    def __init__(self, name: str = '', min_level: int = logging.NOTSET, max_level: Optional[int] = None):
        super().__init__(name)
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        if self.max_level is not None:
            return self.min_level <= record.levelno <= self.max_level
        return record.levelno >= self.min_level


class ContextFilter(logging.Filter):
    """
    Adds custom context data to log records.
    """

    def __init__(self, name: str = '', **context):
        super().__init__(name)
        self.context = context

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self.context.items():
            if callable(value):
                setattr(record, key, value())
            else:
                setattr(record, key, value)
        return True


@lru_cache(maxsize=1024)
def get_relative_path(absolute_path: str, base_dir: Optional[str] = None) -> str:
    """
    Get path relative to base directory with caching for performance.
    
    Args:
        absolute_path: The absolute path to convert
        base_dir: Base directory to make path relative to (defaults to settings.BASE_DIR)
        
    Returns:
        Relative path as a string
    """
    base = base_dir or getattr(settings, 'BASE_DIR', None)
    if not base:
        return absolute_path

    try:
        return os.path.relpath(absolute_path, base)
    except ValueError:
        return absolute_path
