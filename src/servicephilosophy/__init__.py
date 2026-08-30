"""Factory-aware service repository foundation."""

from __future__ import annotations

from servicephilosophy.exceptions import FactoryRequiredError, ServicePhilosophyError
from servicephilosophy.protocols import RepositoryFactoryProtocol, ServiceRepositoryProtocol
from servicephilosophy.repository import ServiceRepository

__all__ = [
    "FactoryRequiredError",
    "RepositoryFactoryProtocol",
    "ServicePhilosophyError",
    "ServiceRepository",
    "ServiceRepositoryProtocol",
    "__version__",
]

__version__ = "0.1.1"
