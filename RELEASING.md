# Releasing `servicephilosophy`

Standalone repository: [SignalSafeSoftware/servicephilosophy](https://github.com/SignalSafeSoftware/servicephilosophy).

## CI publish policy

- **Checks and tests** run on every pull request.
- **`scan` (SonarCloud)** on pull requests is **optional** — it runs only when the PR has the **`scan`** label. On **`push`** (including **`v*`** tag pushes) and **`workflow_dispatch`**, **`scan`** runs automatically.
- **Fork pull requests never run `scan`** — secrets are not exposed to untrusted code.
- **Publish does not run** from pull requests.
- **Publish runs** when:
  - **Manual:** GitHub Actions → **CI** → **Run workflow** on branch **`main`**, or
  - **Tag:** push a semver tag matching `v*` (for example `v0.1.0`).
- **Publish requires** successful **`checks`**, **`tests`**, **`scan`**, and **`smoke-package`** jobs in the same workflow run (see [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)).
- On publish events, **`scan` always runs**; if **`PACKAGES_SONAR_TOKEN`** is missing, the workflow fails at a preflight step with an explicit error.

### SonarCloud secret

This org uses a shared SonarCloud token secret named **`PACKAGES_SONAR_TOKEN`**. Configure it at the organization or repository level. The scan job maps it to the `SONAR_TOKEN` environment variable expected by the SonarCloud action.

### SonarCloud one-time setup (required)

After creating the SonarCloud project **`SignalSafeSoftware_servicephilosophy`**:

1. Open **Analysis Method** for the project:  
   https://sonarcloud.io/project/analysis_method?id=SignalSafeSoftware_servicephilosophy

2. **Disable Automatic Analysis.**  
   CI runs analysis via GitHub Actions (`.github/workflows/ci.yml`). SonarCloud rejects CI analysis when Automatic Analysis is also enabled:

   ```text
   ERROR You are running CI analysis while Automatic Analysis is enabled.
   Please consider disabling one or the other.
   ```

3. Confirm **`sonar-project.properties`** matches the project key (`SignalSafeSoftware_servicephilosophy`) and organization (`signalsafesoftware`).

4. Re-run the failed **CI** workflow on **`main`** (or push an empty commit) to verify the **Scan** job succeeds.

This matches other SignalSafe Python packages (for example `sqlphilosophy`) that use CI-based SonarCloud analysis only.

## Before you release

1. Bump version in [`pyproject.toml`](./pyproject.toml) (`[project].version`).
2. Update [CHANGELOG.md](./CHANGELOG.md) when present.
3. Run locally (matches CI checks):

   ```bash
   uv sync --extra dev
   uv lock --check
   uv run ruff check src tests
   uv run ruff format --check src tests
   uv run mypy src --install-types --non-interactive
   uv run bandit -r src -q -x ./tests,./.venv
   uv run pytest -q
   uv run python scripts/smoke_package.py
   ```

## Publish

1. Commit version updates on **`main`** and push.
2. Tag and push:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

## One-time PyPI setup

1. Register **`servicephilosophy`** on PyPI.
2. On PyPI → project **Publishing** → **Add a new pending publisher**:

   | Field | Value |
   | ----- | ----- |
   | Project name | `servicephilosophy` |
   | Publisher platform | GitHub Actions |
   | Owner | `SignalSafeSoftware` |
   | Repository name | `servicephilosophy` |
   | Workflow filename | `ci.yml` |
   | Environment name | `pypi` |

3. Create GitHub Environment **`pypi`** in repository settings (no secrets required for trusted publishing).
