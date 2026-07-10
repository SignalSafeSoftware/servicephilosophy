"""Typing fixtures for ServiceRepository; checked by mypy via pytest."""

from __future__ import annotations

from servicephilosophy.repository import ServiceRepository


class DummyFactory:
    def value(self) -> str:
        return "ok"


class DummyServiceRepository(ServiceRepository[DummyFactory]):
    def run(self) -> str:
        return self.factory.value()


def typed_run() -> str:
    return DummyServiceRepository(DummyFactory()).run()
