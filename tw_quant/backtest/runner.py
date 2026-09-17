from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..market import KBar
from ..strategy import Decision, StrategyRuntime


@dataclass(frozen=True)
class BacktestResult:
    decisions: tuple[Decision, ...]

    @property
    def signal_count(self) -> int:
        return sum(decision.side != "flat" for decision in self.decisions)


def run_backtest(bars: Sequence[KBar], runtime: StrategyRuntime) -> BacktestResult:
    decisions = tuple(runtime.on_closed_bar(bars[:index]) for index in range(1, len(bars) + 1))
    return BacktestResult(decisions)
