# servicePhilosophy current state — 2026-11-15

Source candidate: 0.1.3, based on remote main 6c72e072112892951eb3ddbbff1aa2d6c4ca0740. Public registry baseline verified as 0.1.2. This is a documentation and version refresh; production source is unchanged. Publication and consumer adoption are separate recorded checks.

The library supplies typed factory-aware repository composition. It does not open sessions, select databases, issue SQL, commit transactions, authorize users or choose tenants. Runtime dependencies remain empty. Factories and application services own those decisions.

Run the [standalone example](examples/factory_service.py), package checks and [release gates](../RELEASING.md). Older ecosystem notes about customer subdomains describe host plans, not library responsibilities.
