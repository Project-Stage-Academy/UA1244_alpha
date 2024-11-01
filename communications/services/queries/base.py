from abc import ABC, abstractmethod


class BaseQuery(ABC):
    @abstractmethod
    async def handle(self, *args, **kwargs):
        """Execute the query and return the result."""
        ...
