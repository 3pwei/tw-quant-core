from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class PaperFill:
    ts: datetime
    side: Literal["buy", "sell"]
    quantity: int
    price: float


@dataclass
class PaperAccount:
    cash: float
    position: int = 0

    def execute(self, fill: PaperFill) -> None:
        if fill.quantity < 1 or fill.price <= 0:
            raise ValueError("quantity and price must be positive")
        signed = fill.quantity if fill.side == "buy" else -fill.quantity
        cost = signed * fill.price
        if fill.side == "buy" and cost > self.cash:
            raise ValueError("insufficient paper cash")
        self.position += signed
        self.cash -= cost
