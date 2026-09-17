from datetime import datetime, timezone

import tw_quant
from tw_quant.backtest import run_backtest
from tw_quant.market import KBar
from tw_quant.paper import PaperAccount, PaperFill
from tw_quant.replay import ReplayEngine
from tw_quant.strategy import MovingAverageCross, StrategyRuntime


def bars():
    result = []
    for i in range(6):
        timestamp = datetime(2026, 1, 1, 0, i, tzinfo=timezone.utc)
        result.append(
            KBar(
                symbol="SYNTH",
                contract="SYNTH-01",
                time=timestamp,
                open=100 + i,
                high=101 + i,
                low=99 + i,
                close=100 + i,
                volume=10,
                status="closed",
                session="day",
                trading_date=timestamp.date(),
                first_tick_time=timestamp,
                last_tick_time=timestamp,
                exchange_time=timestamp,
                received_time=timestamp,
                latency_ms=0,
            )
        )
    return result


def test_package_imports():
    assert tw_quant.StrategyRuntime


def test_backtest_and_replay_are_standalone():
    source = bars()
    result = run_backtest(source, StrategyRuntime(MovingAverageCross()))
    seen = []
    assert result.signal_count > 0
    assert ReplayEngine(reversed(source)).run(seen.append) == len(source)
    assert seen == source


def test_paper_account_uses_synthetic_fills():
    account = PaperAccount(cash=1000)
    account.execute(PaperFill(datetime.now(timezone.utc), "buy", 2, 100))
    assert account.cash == 800
    assert account.position == 2
