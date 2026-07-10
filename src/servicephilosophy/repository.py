"""Factory-aware base class for service repositories without a domain model."""

from __future__ import annotations

from abc import ABC

from servicephilosophy.exceptions import FactoryRequiredError


class ServiceRepository[FactoryT](ABC):  # noqa: B024 — extension point for service subclasses
    """Neutral factory-aware base for service-layer repositories.

    Unlike data repositories, this type does **not** bind to a model or
    persistence backend. Subclasses add domain methods and access the shared
    factory through ``factory``, ``maybe_factory``, or ``has_factory``.
    """

    def __init__(self, factory: FactoryT | None = None) -> None:
        self._factory: FactoryT | None = factory

    @property
    def factory(self) -> FactoryT:
        if self._factory is None:
            raise FactoryRequiredError("factory is required for this operation")
        return self._factory

    @property
    def maybe_factory(self) -> FactoryT | None:
        return self._factory

    @property
    def has_factory(self) -> bool:
        return self._factory is not None
