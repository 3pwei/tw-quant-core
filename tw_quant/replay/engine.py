from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from ..market import KBar


@dataclass
class ReplayEngine:
    bars: Iterable[KBar]

    def run(self, on_bar: Callable[[KBar], None]) -> int:
        count = 0
        for bar in sorted(self.bars, key=lambda item: item.time):
            on_bar(bar)
            count += 1
        return count
