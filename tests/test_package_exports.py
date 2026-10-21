"""Tests for public package exports."""

from __future__ import annotations

import tomllib
from pathlib import Path

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


def test_source_and_project_versions_agree() -> None:
    """A release cannot drift between the two owned version authorities."""
    project = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())["project"]
    assert servicephilosophy.__version__ == project["version"]
