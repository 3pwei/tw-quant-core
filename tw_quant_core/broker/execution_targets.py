from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .identity import BrokerAccountRef


class ExecutionTargetStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class ExecutionTarget:
    """Broker-neutral routing metadata; never carries credentials."""

    target_id: str
    account_ref: BrokerAccountRef
    status: ExecutionTargetStatus = ExecutionTargetStatus.ACTIVE
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id is required")
