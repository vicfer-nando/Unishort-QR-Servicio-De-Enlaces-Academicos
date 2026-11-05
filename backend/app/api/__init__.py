"""Capa HTTP versionada de UniShort QR."""

from .v1 import router as v1_router

__all__ = ["v1_router"]
