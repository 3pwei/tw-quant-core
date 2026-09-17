from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal

OrderSide = Literal["buy", "sell"]
OrderType = Literal["market", "limit", "stop"]


class ExecutionMode(str, Enum):
    PAPER = "paper"
    EXTERNAL = "external"


class BrokerOrderStatus(str, Enum):
    CREATED = "created"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

    @property
    def terminal(self) -> bool:
        return self in {self.FILLED, self.CANCELLED, self.REJECTED}


@dataclass(frozen=True)
class BrokerOrderRequest:
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    mode: ExecutionMode = ExecutionMode.PAPER
    order_type: OrderType = "market"
    limit_price: float | None = None
    stop_price: float | None = None
    reduce_only: bool = False

    def __post_init__(self) -> None:
        if not self.client_order_id.strip() or not self.symbol.strip():
            raise ValueError("client_order_id and symbol are required")
        if self.quantity < 1:
            raise ValueError("quantity must be positive")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit orders require limit_price")
        if self.order_type == "stop" and self.stop_price is None:
            raise ValueError("stop orders require stop_price")


@dataclass(frozen=True)
class BrokerOrder:
    request: BrokerOrderRequest
    status: BrokerOrderStatus
    updated_at: datetime
    broker_order_id: str | None = None
    filled_quantity: int = 0
    average_fill_price: float | None = None

    def __post_init__(self) -> None:
        if self.updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")
        if not 0 <= self.filled_quantity <= self.request.quantity:
            raise ValueError("filled_quantity must be within requested quantity")
