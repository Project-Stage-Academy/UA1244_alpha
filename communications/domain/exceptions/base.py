from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationException(Exception):
    detail: str = "Application error"

    @property
    def message(self) -> str:
        return self.detail

    def __str__(self) -> str:
        return self.message
