"""Tests for ServiceRepository factory wiring."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import assert_type

import pytest

from servicephilosophy.exceptions import FactoryRequiredError
from servicephilosophy.repository import ServiceRepository


class DummyFactory:
    def value(self) -> str:
        return "ok"


class DummyServiceRepository(ServiceRepository[DummyFactory]):
    def run(self) -> str:
        return self.factory.value()


class InvoiceFactory:
    def open_count(self) -> int:
        return 7


class InvoiceService(ServiceRepository[InvoiceFactory]):
    def total_open(self) -> int:
        return self.factory.open_count()


def test_factory_property_returns_configured_factory() -> None:
    factory = DummyFactory()
    repository = ServiceRepository[DummyFactory](factory=factory)
    assert repository.factory is factory


def test_maybe_factory_returns_factory_when_present() -> None:
    factory = DummyFactory()
    repository = ServiceRepository[DummyFactory](factory=factory)
    assert repository.maybe_factory is factory


def test_has_factory_is_true_when_factory_exists() -> None:
    factory = DummyFactory()
    repository = ServiceRepository[DummyFactory](factory=factory)
    assert repository.has_factory is True


def test_has_factory_is_false_without_factory() -> None:
    repository = ServiceRepository[DummyFactory]()
    assert repository.has_factory is False


def test_maybe_factory_returns_none_when_missing() -> None:
    repository = ServiceRepository[DummyFactory]()
    assert repository.maybe_factory is None


def test_factory_property_raises_when_missing() -> None:
    repository = ServiceRepository[DummyFactory]()
    with pytest.raises(FactoryRequiredError, match="factory is required for this operation"):
        _ = repository.factory


def test_subclass_calls_business_logic_through_factory() -> None:
    service = InvoiceService(factory=InvoiceFactory())
    assert service.total_open() == 7


def test_no_domain_model_is_required() -> None:
    repository = DummyServiceRepository(DummyFactory())
    assert not hasattr(ServiceRepository, "model")
    assert not hasattr(repository, "model")
    assert repository.run() == "ok"


def test_typed_dummy_service_repository_run() -> None:
    assert DummyServiceRepository(DummyFactory()).run() == "ok"


def test_factory_property_types() -> None:
    factory = DummyFactory()
    repository = DummyServiceRepository(factory=factory)
    assert_type(repository.factory, DummyFactory)
    assert_type(repository.maybe_factory, DummyFactory | None)
    assert_type(repository.has_factory, bool)


def test_mypy_typing_fixtures() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "tests/typing", "--strict"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
