"""Limitador de tasa efímero en memoria.

La clave es una IP de cliente usada solo durante la ventana y nunca se
persiste ni se asocia a un enlace almacenado.
"""

import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class _Window:
    """Estado de una ventana fija para una clave efímera."""

    started_at: float
    count: int


class FixedWindowRateLimiter:
    """Limitador de ventana fija con expiración automática de entradas.

    Parameters
    ----------
    max_requests:
        Número de solicitudes permitidas por ventana.
    window_seconds:
        Duración de la ventana en segundos. Debe ser menor o igual a 60.
    clock:
        Reloj monotónico inyectable para pruebas deterministas.
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_requests < 1:
            raise ValueError("max_requests debe ser positivo")
        if not 1 <= window_seconds <= 60:
            raise ValueError("window_seconds debe estar entre 1 y 60")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._windows: Dict[str, _Window] = {}
        self._lock = threading.RLock()

    def _current_window(self, key: str, now: float) -> _Window:
        """Obtiene o reinicia la ventana activa de una clave."""

        window = self._windows.get(key)
        if window is None or now - window.started_at >= self.window_seconds:
            window = _Window(started_at=now, count=0)
            self._windows[key] = window
        return window

    def check(self, key: str) -> bool:
        """Consume una unidad del límite.

        Parameters
        ----------
        key:
            Clave efímera del cliente.

        Returns
        -------
        bool
            ``True`` si la solicitud está permitida; ``False`` si se superó el
            límite de la ventana.
        """

        now = self._clock()
        with self._lock:
            window = self._current_window(key, now)
            if window.count >= self.max_requests:
                return False
            window.count += 1
            return True

    def retry_after(self, key: str) -> int:
        """Calcula los segundos restantes de la ventana de una clave."""

        now = self._clock()
        with self._lock:
            window = self._windows.get(key)
            if window is None:
                return 0
            remaining = self.window_seconds - (now - window.started_at)
            return max(0, int(remaining) + (1 if remaining % 1 else 0))

    def reset(self, key: Optional[str] = None) -> None:
        """Elimina el estado de una clave o de todo el limitador."""

        with self._lock:
            if key is None:
                self._windows.clear()
            else:
                self._windows.pop(key, None)

    def active_keys(self) -> int:
        """Devuelve el número de ventanas en memoria (para pruebas)."""

        with self._lock:
            return len(self._windows)
