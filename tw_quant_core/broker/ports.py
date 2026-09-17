from __future__ import annotations

from typing import Mapping, Protocol, runtime_checkable

from .models import BrokerOrder, BrokerOrderRequest


@runtime_checkable
class BrokerPort(Protocol):
    """Public adapter contract. Implementations and credentials live elsewhere."""

    broker_name: str

    async def submit_order(self, order: BrokerOrderRequest) -> BrokerOrder: ...

    async def cancel_order(self, order: BrokerOrder) -> BrokerOrder: ...

    async def refresh_order(self, order: BrokerOrder) -> BrokerOrder: ...

    async def account_state(self) -> Mapping[str, object]: ...
