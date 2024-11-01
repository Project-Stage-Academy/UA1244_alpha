from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseCommand(ABC):
    @abstractmethod
    def handle(self, *args, **kwargs):
        ...
