"""Tests for servicephilosophy protocols."""

from __future__ import annotations

import pytest

from servicephilosophy.exceptions import FactoryRequiredError
from servicephilosophy.protocols import RepositoryFactoryProtocol, ServiceRepositoryProtocol
from servicephilosophy.repository import ServiceRepository


class DummyFactory(RepositoryFactoryProtocol):
    pass


class DummyService(ServiceRepository[DummyFactory]):
    def label(self) -> str:
        return "dummy"


def test_service_repository_satisfies_protocol_with_factory() -> None:
    factory = DummyFactory()
    service = DummyService(factory=factory)
    repo: ServiceRepositoryProtocol[DummyFactory] = service

    assert repo.has_factory is True
    assert repo.maybe_factory is factory
    assert repo.factory is factory
    assert service.label() == "dummy"


def test_service_repository_satisfies_protocol_without_factory() -> None:
    service = DummyService()
    repo: ServiceRepositoryProtocol[DummyFactory] = service

    assert repo.has_factory is False
    assert repo.maybe_factory is None
    with pytest.raises(FactoryRequiredError, match="factory is required for this operation"):
        _ = repo.factory


def test_dummy_factory_satisfies_repository_factory_protocol() -> None:
    factory = DummyFactory()
    protocol: RepositoryFactoryProtocol = factory
    assert protocol is factory


def test_structural_factory_satisfies_repository_factory_protocol() -> None:
    class SessionFactory:
        def get_service(
            self,
            service_class: type[ServiceRepository[SessionFactory]],
        ) -> ServiceRepository[SessionFactory]:
            return service_class(factory=self)

    factory = SessionFactory()
    protocol: RepositoryFactoryProtocol = factory
    assert protocol is factory
