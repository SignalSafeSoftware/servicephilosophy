"""Tests for public package exports."""

from __future__ import annotations

import servicephilosophy


def test_public_exports() -> None:
    assert servicephilosophy.__all__ == [
        "FactoryRequiredError",
        "RepositoryFactoryProtocol",
        "ServicePhilosophyError",
        "ServiceRepository",
        "ServiceRepositoryProtocol",
        "__version__",
    ]
    assert servicephilosophy.ServiceRepository is not None
    assert servicephilosophy.FactoryRequiredError is not None
    assert servicephilosophy.RepositoryFactoryProtocol is not None
    assert servicephilosophy.ServiceRepositoryProtocol is not None
    assert servicephilosophy.ServicePhilosophyError is not None
