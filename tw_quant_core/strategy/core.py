from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Protocol, Sequence

from ..market import KBar

Side = Literal["buy", "sell", "flat"]


@dataclass(frozen=True)
class Decision:
    side: Side
    reason: str
    quantity: int = 0


class Strategy(Protocol):
    def evaluate(self, bars: Sequence[KBar]) -> Decision: ...


@dataclass
class StrategyRuntime:
    strategy: Strategy

    def on_closed_bar(self, bars: Sequence[KBar]) -> Decision:
        if not bars:
            return Decision("flat", "no closed bars")
        return self.strategy.evaluate(tuple(bars))


@dataclass
class CompositeStrategy:
    strategies: Iterable[Strategy]

    def evaluate(self, bars: Sequence[KBar]) -> Decision:
        decisions = [strategy.evaluate(bars) for strategy in self.strategies]
        active = [decision for decision in decisions if decision.side != "flat"]
        if not active:
            return Decision("flat", "no component signal")
        sides = {decision.side for decision in active}
        if len(sides) != 1:
            return Decision("flat", "component disagreement")
        return Decision(active[0].side, "component consensus", min(d.quantity for d in active))


@dataclass(frozen=True)
class MovingAverageCross:
    fast_window: int = 3
    slow_window: int = 5
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.fast_window < 1 or self.slow_window <= self.fast_window:
            raise ValueError("require 1 <= fast_window < slow_window")
        if self.quantity < 1:
            raise ValueError("quantity must be positive")

    def evaluate(self, bars: Sequence[KBar]) -> Decision:
        if len(bars) < self.slow_window:
            return Decision("flat", "insufficient history")
        closes = [float(bar.close) for bar in bars]
        fast = sum(closes[-self.fast_window:]) / self.fast_window
        slow = sum(closes[-self.slow_window:]) / self.slow_window
        if fast > slow:
            return Decision("buy", "fast average above slow average", self.quantity)
        if fast < slow:
            return Decision("sell", "fast average below slow average", self.quantity)
        return Decision("flat", "averages equal")
