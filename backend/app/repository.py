"""Repositorio de persistencia para enlaces cortos.

Centraliza el acceso a datos y la traducción de fallos de SQLAlchemy a errores
de dominio. Las escrituras se confirman o revierten completas.
"""

from datetime import datetime
from typing import Callable, List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .domain import generate_short_code, utc_now
from .errors import CollisionExhaustedError, PersistenceError
from .models import ShortURL

MAX_COLLISION_ATTEMPTS = 10
CodeGenerator = Callable[[], str]


def _new_code_factory(length: int) -> CodeGenerator:
    """Construye un generador de códigos con la longitud configurada."""

    return lambda: generate_short_code(length)


def create_link(
    session: Session,
    original_url: str,
    expires_at: Optional[datetime] = None,
    code_length: int = 7,
    code_generator: Optional[CodeGenerator] = None,
) -> ShortURL:
    """Persiste un enlace nuevo, reintentando ante colisiones de código.

    Parameters
    ----------
    session:
        Sesión de SQLAlchemy controlada por el caso de uso.
    original_url:
        URL de destino ya validada.
    expires_at:
        Fecha opcional de caducidad en UTC.
    code_length:
        Longitud del código cuando no se inyecta un generador.
    code_generator:
        Generador alternativo, útil para pruebas de colisión.

    Returns
    -------
    ShortURL
        Enlace persistido y refrescado.

    Raises
    ------
    CollisionExhaustedError
        Si tras los reintentos no se consigue un código libre.
    PersistenceError
        Si falla la base de datos por una causa distinta a la colisión.
    """

    generator = code_generator or _new_code_factory(code_length)

    for _ in range(MAX_COLLISION_ATTEMPTS):
        link = ShortURL(
            short_code=generator(),
            original_url=original_url,
            created_at=utc_now(),
            is_active=True,
            expires_at=expires_at,
            click_count=0,
        )
        session.add(link)
        try:
            session.commit()
            session.refresh(link)
            return link
        except IntegrityError:
            session.rollback()
            continue
        except SQLAlchemyError as error:
            session.rollback()
            raise PersistenceError from error

    raise CollisionExhaustedError


def get_by_code(session: Session, short_code: str) -> Optional[ShortURL]:
    """Busca un enlace por su código corto.

    Parameters
    ----------
    session:
        Sesión activa.
    short_code:
        Código solicitado.

    Returns
    -------
    Optional[ShortURL]
        Enlace encontrado o ``None``.
    """

    return session.scalar(select(ShortURL).where(ShortURL.short_code == short_code))


def list_links(session: Session, limit: int = 50, offset: int = 0) -> List[ShortURL]:
    """Devuelve enlaces ordenados del más reciente al más antiguo."""

    statement = (
        select(ShortURL)
        .order_by(ShortURL.created_at.desc())
        .offset(max(offset, 0))
        .limit(max(1, limit))
    )
    return list(session.scalars(statement).all())


def count_links(session: Session) -> int:
    """Cuenta el total de enlaces almacenados."""

    return int(session.scalar(select(func.count(ShortURL.id))) or 0)


def increment_click_count(session: Session, short_code: str) -> None:
    """Incrementa de forma atómica el contador agregado de un enlace.

    Parameters
    ----------
    session:
        Sesión activa.
    short_code:
        Código del enlace redirigido.

    Raises
    ------
    PersistenceError
        Si la actualización falla; el servicio puede decidir continuar con la
        redirección.
    """

    statement = (
        update(ShortURL)
        .where(ShortURL.short_code == short_code)
        .values(click_count=ShortURL.click_count + 1)
    )
    try:
        session.execute(statement)
        session.commit()
    except SQLAlchemyError as error:
        session.rollback()
        raise PersistenceError from error


def update_link(
    session: Session,
    link: ShortURL,
    is_active: Optional[bool] = None,
    expires_at: Optional[datetime] = None,
    update_expiration: bool = False,
) -> ShortURL:
    """Actualiza el estado y/o la expiración de un enlace existente.

    Parameters
    ----------
    session:
        Sesión activa.
    link:
        Enlace previamente recuperado.
    is_active:
        Nuevo estado, si se desea modificar.
    expires_at:
        Nueva fecha de expiración.
    update_expiration:
        Indica si ``expires_at`` debe escribirse, incluso con valor ``None``.

    Returns
    -------
    ShortURL
        Enlace actualizado.

    Raises
    ------
    PersistenceError
        Si el guardado falla; la transacción se revierte.
    """

    if is_active is not None:
        link.is_active = is_active
    if update_expiration:
        link.expires_at = expires_at
    try:
        session.commit()
        session.refresh(link)
        return link
    except SQLAlchemyError as error:
        session.rollback()
        raise PersistenceError from error
