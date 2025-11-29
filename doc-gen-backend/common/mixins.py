import uuid
from typing import List

from django.db import models
from django.utils.text import slugify


class CacheKeyMixin:
    def get_cache_key(self, request, view_name):
        # Create a unique cache key based on user and query parameters
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        params = request.query_params.urlencode()
        return f'{view_name}_{user_id}_{params}'


class SlugGeneratorMixin:
    """
    A mixin to automatically generate slugs for model instances.
    """

    def generate_unique_slug(self) -> str:
        """
        Generate a unique slug for the model instance.
        Uses the get_slug_fields() method to determine which fields to use for slug generation.
        """
        if not self.get_slug_fields():
            raise NotImplementedError(
                f"Model {self.__class__.__name__} must implement get_slug_fields()"
            )

        # Get the base slug from concatenated fields
        slug_parts = []
        for field in self.get_slug_fields():
            value = getattr(self, field, None)
            if value is not None:
                # Handle foreign key fields: assume __str__ or look for specific attributes
                if isinstance(value, models.Model) and hasattr(value, '__str__'):
                    slug_parts.append(str(value))
                elif hasattr(value, 'name'):  # Common for models with a 'name' field
                    slug_parts.append(str(value.name))
                else:
                    slug_parts.append(str(value))

        # Handle case where slug_parts might be empty
        raw_slug = " ".join(filter(None, slug_parts)).strip()

        # Apply Django's slugify to convert to proper slug format
        base_slug = slugify(raw_slug)

        # Handle empty slug case
        if not base_slug:
            base_slug = "item"

        # If no modifications needed, return the base slug
        if not self.pk:  # New instance
            if not self.__class__.objects.filter(slug=base_slug).exists():
                return base_slug
        else:  # Existing instance
            if not self.__class__.objects.exclude(pk=self.pk).filter(slug=base_slug).exists():
                return base_slug

        # Generate unique slug by appending counter
        counter = 0
        while True:
            # Use a UUID fragment for better uniqueness and less predictable slugs
            unique_suffix = uuid.uuid4().hex[:8]  # Shorter, 8 chars is usually sufficient
            test_slug = f"{base_slug}-{unique_suffix}"
            if self._is_slug_unique(test_slug):
                return test_slug
            counter += 1
            if counter > 50:  # Fail-safe to prevent infinite loops in extreme edge cases
                raise ValueError(f"Failed to generate unique slug for {self.pk} after {counter} attempts.")

    def _is_slug_unique(self, slug: str) -> bool:
        """
        Checks if the given slug is unique, excluding the current instance if it exists.
        """
        queryset = self.__class__.objects.filter(slug=slug)
        if self.pk:  # If it's an existing instance, exclude itself
            queryset = queryset.exclude(pk=self.pk)
        return not queryset.exists()

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug if it's not set.
        """
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def get_slug_fields(self) -> List[str]:
        """
        Abstract method to be implemented by models using this mixin.
        Should return a list of field names (strings) to be used for slug generation.
        Example: ['title', 'category__name']
        """
        raise NotImplementedError(
            f"Model {self.__class__.__name__} must implement get_slug_fields()"
        )
