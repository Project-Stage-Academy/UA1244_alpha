import logging
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


logger = logging.getLogger('django')

@dataclass
class BaseEntity(ABC):
    oid: str = field(
        default_factory=lambda: str(uuid4()),
        kw_only=True,
    )
    created_at: datetime = field(
        default_factory=datetime.now,
        kw_only=True,
    )


    def __post_init__(self):
        logger.info(f"Created new entity: {self.__class__.__name__} with oid {self.oid} at {self.created_at}")
