# ServiceFactory composition — all three layers

Example of how an **application** wires together the three repository layers:

| Layer | Package | Role |
|-------|---------|------|
| Factory-aware base | [servicePhilosophy](https://github.com/SignalSafeSoftware/servicephilosophy) | Optional factory wiring; no model, SQL, or HTTP |
| SQL persistence | [sqlPhilosophy](https://github.com/SignalSafeSoftware/sqlphilosophy) | Model-bound repositories (`BaseRepository`) |
| HTTP resources | apiPhilosophy (proposed) | OpenAPI/Swagger resource repositories (`BaseApiRepository`) |
| Business logic | *your application* | Service repositories (`ServiceRepository` subclasses) |

This document is illustrative. apiPhilosophy types are shown as proposed; sqlPhilosophy and servicePhilosophy APIs match current packages.

---

## Architecture

One **request-scoped** `ServiceFactory` exposes three namespaces:

```text
ServiceFactory
  .repositories -> sqlPhilosophy repositories   (database)
  .api          -> apiPhilosophy repositories   (remote HTTP)
  .services     -> business service repositories (domain logic)
```

Each namespace is itself a small factory that caches typed repository instances and receives a back-reference to the root `ServiceFactory` so repos can reach sibling layers.

```text
                    ServiceFactory
                   /       |        \
                  /        |         \
     RepositoryFactory  ApiRepositoryFactory  ServiceRepositoryFactory
     (sqlPhilosophy)    (apiPhilosophy)      (application)
            |                  |                      |
     UserRepository      UserApiRepository    PermissionServiceRepository
     (User model)        (UserDto)            (no model)
```

---

## Root factory

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from apiphilosophy.client import ApiClient


@dataclass
class RequestContext:
    """Per-request metadata (actor, tenant, trace id, …)."""

    actor_id: int


class ServiceFactory:
    """Request-scoped composition root for SQL, API, and service repositories."""

    def __init__(
        self,
        db_session: Session,
        api_client: ApiClient,
        context: RequestContext,
    ) -> None:
        self._context = context
        self.repositories = RepositoryFactory(db_session, self)
        self.api = ApiRepositoryFactory(api_client, self)
        self.services = ServiceRepositoryFactory(self)

    @property
    def context(self) -> RequestContext:
        return self._context
```

- **`db_session`** — SQLAlchemy session (sqlPhilosophy)
- **`api_client`** — HTTP transport (apiPhilosophy)
- **`context`** — application request context (not owned by any library)

Sub-factories take `self` so every repository can call `self.factory.repositories…`, `self.factory.api…`, or `self.factory.services…`.

---

## Namespace factories (sketch)

### SQL — `RepositoryFactory`

```python
from sqlphilosophy.sync.repository import BaseRepository


class RepositoryFactory:
    def __init__(self, session: Session, root: ServiceFactory) -> None:
        self._session = session
        self._root = root
        self._cache: dict[type, BaseRepository] = {}

    def users(self) -> UserRepository:
        return self._cached(UserRepository)

    def project_memberships(self) -> ProjectMembershipRepository:
        return self._cached(ProjectMembershipRepository)

    def _cached[R](self, repo_class: type[R]) -> R:
        cached = self._cache.get(repo_class)
        if cached is None:
            cached = repo_class(self._session, self._root)
            self._cache[repo_class] = cached
        return cached  # type: ignore[return-value]
```

### API — `ApiRepositoryFactory`

```python
from apiphilosophy.repository import BaseApiRepository


class ApiRepositoryFactory:
    def __init__(self, client: ApiClient, root: ServiceFactory) -> None:
        self._client = client
        self._root = root
        self._cache: dict[type, BaseApiRepository] = {}

    def users(self) -> UserApiRepository:
        return self._cached(UserApiRepository)

    def _cached[R](self, repo_class: type[R]) -> R:
        cached = self._cache.get(repo_class)
        if cached is None:
            cached = repo_class(client=self._client, factory=self._root)
            self._cache[repo_class] = cached
        return cached  # type: ignore[return-value]
```

### Services — `ServiceRepositoryFactory`

```python
from servicephilosophy import ServiceRepository


class ServiceRepositoryFactory:
    def __init__(self, root: ServiceFactory) -> None:
        self._root = root
        self._cache: dict[type, ServiceRepository] = {}

    def permissions(self) -> PermissionServiceRepository:
        return self._cached(PermissionServiceRepository)

    def _cached[R](self, repo_class: type[R]) -> R:
        cached = self._cache.get(repo_class)
        if cached is None:
            cached = repo_class(factory=self._root)
            self._cache[repo_class] = cached
        return cached  # type: ignore[return-value]
```

---

## Usage

Construct one factory per request (or unit of work), then call the namespace that matches the concern:

```python
factory = ServiceFactory(db_session=session, api_client=client, context=context)

# Business logic — no model, composes SQL + API as needed
allowed = factory.services.permissions().has_permission(
    actor_id=factory.context.actor_id,
    permission="project:read",
    resource_id=project_id,
)

# Remote HTTP resource
remote_user = factory.api.users().get(id=123)

# Local database entity
local_user = factory.repositories.users().get(123)
```

Typical call flow:

1. **Controller / handler** obtains session, API client, and context.
2. **ServiceFactory** is created once for that scope.
3. **Service repositories** implement use-case methods and delegate persistence to `.repositories` and remote calls to `.api`.
4. **SQL and API repositories** stay thin — CRUD and wire mapping only.

---

## Service repository with no model

Business rules live in `ServiceRepository` subclasses. They do **not** bind to an ORM model or OpenAPI DTO type at the base level; they only need the root factory.

```python
from servicephilosophy import ServiceRepository


class PermissionServiceRepository(ServiceRepository[ServiceFactory]):
    def has_permission(
        self,
        actor_id: int,
        permission: str,
        resource_id: int,
    ) -> bool:
        membership = self.factory.repositories.project_memberships().find_for_actor(
            actor_id=actor_id,
            resource_id=resource_id,
        )

        return membership is not None and membership.has_permission(permission)
```

### Why this shape works

- **`PermissionServiceRepository` has no `model`.** It is not a sqlPhilosophy repository and not an apiPhilosophy resource client.
- **It only needs access to `ServiceFactory`.** Through `self.factory` it reaches SQL repos, API repos, and other service repos without importing transport or ORM details into the base class.
- **SQL repositories handle persistence.** `ProjectMembershipRepository` loads rows, runs queries, and flushes the session.
- **API repositories handle remote resources.** `UserApiRepository.get()` performs HTTP and parses DTOs.
- **Service repositories handle business logic.** Permission checks, onboarding flows, and cross-source aggregation belong here.

---

## Layer responsibilities (summary)

| Call | Layer | Example class | Has model/DTO? |
|------|-------|---------------|----------------|
| `factory.repositories.users().get(123)` | sqlPhilosophy | `UserRepository(BaseRepository[User, …])` | Yes — SQLAlchemy model |
| `factory.api.users().get(id=123)` | apiPhilosophy | `UserApiRepository(BaseApiRepository[UserDto, …])` | Yes — API DTO |
| `factory.services.permissions().has_permission(…)` | application / servicePhilosophy | `PermissionServiceRepository(ServiceRepository[…])` | **No** |

---

## SQL repository (persistence only)

```python
from sqlphilosophy.sync.repository import BaseRepository


class UserRepository(BaseRepository[User, ServiceFactory]):
    def __init__(self, session: Session, factory: ServiceFactory) -> None:
        super().__init__(User, session, factory)

    def get_by_email(self, email: str) -> User | None:
        return self.first(email=email)
```

## API repository (remote resource only)

```python
from apiphilosophy.repository import BaseApiRepository


class UserApiRepository(BaseApiRepository[UserDto, ServiceFactory]):
    def get(self, id: int) -> UserDto:
        payload = self._client.get_json(f"/users/{id}")
        return UserDto(**payload)
```

---

## Dependency direction

```text
servicePhilosophy
  ServiceRepository[FactoryT]

sqlPhilosophy
  BaseRepository[ModelT, FactoryT]
  depends on servicePhilosophy

apiPhilosophy
  BaseApiRepository[ResourceT, FactoryT]
  depends on servicePhilosophy

application
  ServiceFactory, PermissionServiceRepository, UserRepository, UserApiRepository
  depends on all three as needed
```

Libraries never import your application factory. The application composes them.

---

## Related docs

- [servicePhilosophy README](https://github.com/SignalSafeSoftware/servicephilosophy)
- [sqlPhilosophy repository guide](https://github.com/SignalSafeSoftware/sqlphilosophy/blob/main/docs/repository-guide.md)
- [sqlPhilosophy + servicePhilosophy integration](https://github.com/SignalSafeSoftware/sqlphilosophy/blob/main/docs/integration/servicephilosophy.md)
- [apiPhilosophy design document](../../../apiphilosophy/docs/DESIGN.md)
