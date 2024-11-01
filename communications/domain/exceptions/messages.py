from dataclasses import dataclass

from .base import ApplicationException


@dataclass(eq=False)
class TitleTooLongException(ApplicationException):
    text: str = 'Text too long'

    @property
    def message(self):
        return f'Text too long: {self.text[:255]}...'


@dataclass(eq=False)
class EmptyTextException(ApplicationException):
    @property
    def message(self):
        return 'Text is empty'
    