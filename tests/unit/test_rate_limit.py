"""Pruebas unitarias del limitador de tasa efímero."""

import pytest
from app.rate_limit import FixedWindowRateLimiter


def test_allows_requests_up_to_the_limit_and_blocks_the_next(fake_clock):
    limiter = FixedWindowRateLimiter(
        max_requests=3, window_seconds=60, clock=fake_clock
    )
    assert [limiter.check("cliente") for _ in range(3)] == [True, True, True]
    assert limiter.check("cliente") is False


def test_window_resets_after_expiration(fake_clock):
    limiter = FixedWindowRateLimiter(
        max_requests=2, window_seconds=10, clock=fake_clock
    )
    assert limiter.check("cliente") is True
    assert limiter.check("cliente") is True
    assert limiter.check("cliente") is False
    fake_clock.advance(10)
    assert limiter.check("cliente") is True


def test_keys_are_counted_separately(fake_clock):
    limiter = FixedWindowRateLimiter(
        max_requests=1, window_seconds=60, clock=fake_clock
    )
    assert limiter.check("a") is True
    assert limiter.check("b") is True
    assert limiter.check("a") is False


def test_retry_after_and_reset(fake_clock):
    limiter = FixedWindowRateLimiter(
        max_requests=1, window_seconds=30, clock=fake_clock
    )
    limiter.check("cliente")
    fake_clock.advance(5)
    assert 20 <= limiter.retry_after("cliente") <= 25
    limiter.reset("cliente")
    assert limiter.check("cliente") is True
    limiter.reset()
    assert limiter.active_keys() == 0
    assert limiter.retry_after("cliente") == 0


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(max_requests=0)
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(window_seconds=61)


def test_expired_keys_are_removed_even_for_other_clients(fake_clock):
    limiter = FixedWindowRateLimiter(window_seconds=10, clock=fake_clock)
    limiter.check("old-client")
    fake_clock.advance(10)
    limiter.check("new-client")
    assert limiter.active_keys() == 1
    assert limiter.retry_after("old-client") == 0


def test_timer_removes_idle_key_and_stale_timer_keeps_replacement(
    fake_clock, monkeypatch
):
    callbacks = []

    class FakeTimer:
        def __init__(self, interval, function, args):
            self.function = function
            self.args = args
            self.daemon = False
            callbacks.append(self)

        def start(self):
            assert self.daemon is True

        def cancel(self):
            pass

        def fire(self):
            self.function(*self.args)

    monkeypatch.setattr("app.rate_limit.threading.Timer", FakeTimer)
    limiter = FixedWindowRateLimiter(window_seconds=10, clock=fake_clock)
    limiter.check("idle")
    callbacks[0].fire()
    assert limiter.active_keys() == 0
    limiter.check("replaced")
    fake_clock.advance(10)
    limiter.check("replaced")
    callbacks[1].fire()
    assert limiter.active_keys() == 1
    limiter.reset("missing")
    limiter.reset()
