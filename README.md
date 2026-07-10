# servicePhilosophy

A small typed foundation for factory-aware repository-style components.

| | |
|---|---|
| **Python** | 3.12+ |
| **Runtime deps** | none |
| **License** | MIT |

## Core idea

```text
ServiceRepository[FactoryT]
= a neutral base class for objects that need factory access.
It does not require a model.
It does not know about SQL, HTTP, controllers, or frameworks.
```

`ServiceRepository` stores an optional factory and exposes it through:

- **`factory`** — returns the factory, or raises `FactoryRequiredError` when missing
- **`maybe_factory`** — returns the factory or `None`
- **`has_factory`** — `True` when a factory was provided at construction

Use **`ServiceRepositoryProtocol`** when you want to type against that shape without inheriting from the base class. Use **`RepositoryFactoryProtocol`** as a minimal marker for factory types that downstream packages extend.

## What this is (and is not)

- **`ServiceRepository` is not a SQL repository.**
- **`ServiceRepository` is not an API client.**
- It is a **shared factory-aware base**.
- **[sqlPhilosophy](https://github.com/SignalSafeSoftware/sqlphilosophy)** can extend it with model-bound persistence.
- **apiPhilosophy** can extend it with HTTP/resource clients.
- **Application service repositories** can extend it directly for business logic with no model at all.

This package has zero runtime dependencies. It does not include SQLAlchemy, HTTP clients, FastAPI, Pydantic, or Django.

## Basic service repository

```python
from servicephilosophy import ServiceRepository


class ServiceFactory:
    def greeting(self) -> str:
        return "hello"


class GreetingService(ServiceRepository[ServiceFactory]):
    def greet(self) -> str:
        return self.factory.greeting()
```

## SQL specialization in another package

```python
from typing import Generic, TypeVar

from servicephilosophy import ServiceRepository

ModelT = TypeVar("ModelT")
FactoryT = TypeVar("FactoryT")


class BaseRepository(ServiceRepository[FactoryT], Generic[ModelT, FactoryT]):
    model: type[ModelT]
```

## API specialization in another package

```python
from typing import Generic, TypeVar

from servicephilosophy import ServiceRepository

ResourceT = TypeVar("ResourceT")
FactoryT = TypeVar("FactoryT")


class BaseApiRepository(ServiceRepository[FactoryT], Generic[ResourceT, FactoryT]):
    pass
```

## Business logic with no model

```python
from servicephilosophy import ServiceRepository


class PermissionServiceRepository(ServiceRepository[ServiceFactory]):
    def has_permission(self, actor_id: int, permission: str) -> bool:
        return True
```

## Recommended ecosystem

```text
servicePhilosophy
  ServiceRepository[FactoryT]

sqlPhilosophy
  BaseRepository[ModelT, FactoryT]

apiPhilosophy
  BaseApiRepository[ResourceT, FactoryT]

application
  PermissionServiceRepository(ServiceRepository[ServiceFactory])
```

Each layer adds its own concern. `servicePhilosophy` only handles factory wiring; specialization lives in the package or application that needs it.

## Install

```bash
pip install servicephilosophy
```

Development:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check src tests
uv run mypy src
```

## Public API

```python
from servicephilosophy import (
    FactoryRequiredError,
    RepositoryFactoryProtocol,
    ServiceRepository,
    ServiceRepositoryProtocol,
)
```

Or import from submodules:

```python
from servicephilosophy.repository import ServiceRepository
from servicephilosophy.protocols import RepositoryFactoryProtocol, ServiceRepositoryProtocol
from servicephilosophy.exceptions import FactoryRequiredError
```
