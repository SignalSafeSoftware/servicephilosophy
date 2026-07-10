"""Shared exceptions for servicephilosophy."""


class ServicePhilosophyError(Exception):
    """Base error for servicephilosophy."""


class FactoryRequiredError(ServicePhilosophyError):
    """Raised when an operation requires a factory but none was configured."""
