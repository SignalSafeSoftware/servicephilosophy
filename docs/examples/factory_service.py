"""Run without a database: python docs/examples/factory_service.py."""

from servicephilosophy import FactoryRequiredError, ServiceRepository


class ServiceFactory:
    def greeting(self) -> str:
        return "hello"


class GreetingService(ServiceRepository[ServiceFactory]):
    def greet(self) -> str:
        return self.factory.greeting()


def main() -> None:
    factory = ServiceFactory()
    service = GreetingService(factory)
    assert service.has_factory
    assert service.maybe_factory is factory
    assert service.greet() == "hello"
    unconfigured: GreetingService = GreetingService()
    assert unconfigured.maybe_factory is None
    try:
        unconfigured.greet()
    except FactoryRequiredError:
        return
    raise AssertionError("Factory access must reject an unconfigured service")


if __name__ == "__main__":
    main()
