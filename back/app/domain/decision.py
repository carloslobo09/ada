from dataclasses import dataclass
from enum import Enum


class DecisionStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Decision:
    """Decision final emitida por la plataforma para un caso procesado."""

    status: DecisionStatus
    reason: str
