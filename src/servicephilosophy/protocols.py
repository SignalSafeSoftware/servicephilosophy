"""Protocols for factory-aware service repositories."""

from __future__ import annotations

from typing import Protocol, TypeVar

FactoryT = TypeVar("FactoryT", covariant=True)


class ServiceRepositoryProtocol(Protocol[FactoryT]):
    """Structural typing surface for factory-aware repositories."""

    @property
    def factory(self) -> FactoryT: ...

    @property
    def maybe_factory(self) -> FactoryT | None: ...

    @property
    def has_factory(self) -> bool: ...


class RepositoryFactoryProtocol(Protocol):
    """Marker protocol for repository-scoped factories.

    Intentionally empty so downstream packages can extend it with
    SQL-, API-, or application-specific methods without coupling this
    package to those concerns.
    """
