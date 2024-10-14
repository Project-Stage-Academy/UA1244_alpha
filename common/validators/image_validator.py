from collections.abc import Mapping
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from PIL import Image


@deconstructible
class ImageValidator:
    default_messages = {
        "dimensions": _(
            "Image dimensions should not exceed %(max_width)s x %(max_height)s pixels."
        ),
        "size": _(
            "File size exceeds the allowed limit of %(max_size)s KiB."
        ),
        "invalid_image": _(
            "The uploaded file is not a valid image."
        ),
        "invalid_extension": _(
            "Invalid file extension. Only PNG, JPG, and JPEG are allowed."
        ),
    }

    def __init__(self, max_size=None, max_width=None, max_height=None, messages=None):
        """
        Initialize the image validator with optional size and dimension limits.

        :param max_size: Maximum file size in bytes
        :param max_width: Maximum width in pixels
        :param max_height: Maximum height in pixels
        :param messages: Custom error messages
        """
        self.max_size = max_size
        self.max_width = max_width
        self.max_height = max_height
        if messages is not None and isinstance(messages, Mapping):
            self.messages = {**self.default_messages, **messages}
        else:
            self.messages = self.default_messages

    def __call__(self, value):
        # Validate file extension
        valid_extensions = ('png', 'jpg', 'jpeg')
        if not value.name.lower().endswith(valid_extensions):
            raise ValidationError(
                self.messages['invalid_extension'],
                code='invalid_extension'
            )

        try:
            # Open the image to get its dimensions
            image = Image.open(value)
            image.verify()
            width, height = image.size
        except Exception:
            raise ValidationError(
                self.messages['invalid_image'],
                code='invalid_image'
            )

        # Validate file size
        if self.max_size is not None and value.size > self.max_size:
            raise ValidationError(
                self.messages['size'],
                code='invalid_size',
                params={'max_size': float(self.max_size) / 1024}
            )

        # Validate image dimensions
        self._validate_dimensions(width, height)

    def _validate_dimensions(self, width, height):
        if self.max_width is not None and width > self.max_width:
            self._raise_dimension_error()

        if self.max_height is not None and height > self.max_height:
            self._raise_dimension_error()

    def _raise_dimension_error(self):
        raise ValidationError(
            self.messages['dimensions'],
            code='invalid_dimensions',
            params={
                'max_width': self.max_width,
                'max_height': self.max_height,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, ImageValidator):
            return False
        return (
            self.max_size == other.max_size and
            self.max_width == other.max_width and
            self.max_height == other.max_height and
            self.messages == other.messages
        )
