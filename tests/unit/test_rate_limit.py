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
