# servicePhilosophy current state — 2026-11-15

Current verified release: 0.1.3. [The tag pipeline](https://github.com/SignalSafeSoftware/servicephilosophy/actions/runs/43796773592) passed and anonymous PyPI wheel/sdist readback matched the tagged runtime source at `86b76bb59eefd4830a92c2eb8dfe290f1afce2f2`. Consumer adoption remains a separate check.

The library supplies typed factory-aware repository composition. It does not open sessions, select databases, issue SQL, commit transactions, authorize users or choose tenants. Runtime dependencies remain empty. Factories and application services own those decisions.

Run the [standalone example](examples/factory_service.py), package checks and [release gates](../RELEASING.md). Older ecosystem notes about customer subdomains describe host plans, not library responsibilities.
