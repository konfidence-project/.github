# Konfidence Project - Shared GitHub Organization Files

This repository contains shared files and configurations for the Konfidence Project GitHub organization, including:

- **GitHub Workflows**: Reusable CI/CD workflows for Go projects and Kubebuilder operators
- **GitHub Actions**: Composite actions for common tasks like authentication and building
- **Semantic Release Configuration**: Standardized release automation with conventional commits
- **Renovate Configuration**: Dependency management presets for automated updates
- **Organization Templates**: Pull request templates and other GitHub organization files



## Available Workflows

### 1. Golang Lint ([`golang-lint.yaml`](./.github/workflows/golang-lint.yaml))

Runs golangci-lint on Go projects with private repository access.

**Usage:**
```yaml
jobs:
  lint:
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
    secrets: inherit
```

### 2. Kubebuilder Test ([`kubebuilder-test.yaml`](./.github/workflows/kubebuilder-test.yaml))

Comprehensive testing workflow for Kubebuilder projects with optional Kind cluster setup, CRD installation, and lifecycle hooks for setup and cleanup commands.

> **⚠️ Installation of CRDs ⚠️** 
> 
> With the [current CRDs Repo Setup](https://github.com/konfidence-project/crds), the test job will checkout the [config/crd](https://github.com/konfidence-project/crds/tree/main/config/crd) path and apply them to the kind cluster. Per default, it will use the main branch as ref. When implementing this workflow, make sure that the actual commit or version ref of the repo is used. If the repo supports generating the CRDs with a make command, use the `before-tests` input to generate them instead and make sure that the `install-crds` input is set to `false`.

**Usage:**
```yaml
jobs:
  test:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: true    # Optional: Create Kind cluster (default: true)
      install-crds: true         # Optional: Install CRDs (default: true)
      crds-version: "main"       # Optional: CRD version ref (default: main) 
      test-cmd: "test"           # Optional: Make target to run (default: "test" will execute `make test`)
      before-tests: "make setup"  # Optional: Command to run before tests (e.g., setup commands)
      after-tests: "make cleanup" # Optional: Command to run after tests (e.g., cleanup commands)
```

#### Example Usages:

**Unit Tests**

Following example runs `make test` to run simple go tests, without starting a kind cluster or installing CRDs

```yaml
jobs:
  test-unit:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: false    
      install-crds: false       
      test-cmd: "test"         
```

**Unit Tests and custom CRD generations**

Following example also runs `make test` without a kind cluster, but will run `make generate-test-crds` before executing the tests.

```yaml
jobs:
  test-unit:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: false    
      install-crds: false       
      test-cmd: "test"    
      before-tests: `make generate-test-crds`     
```

**Integration Tests with Kind Cluster**

This example will run the `make test-e2e` command with an existing kind cluster and install the CRDs from commit e029cc3. 

```yaml
jobs:
  test-unit:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: true    
      install-crds: true       
      crds-version: "e029cc3"
      test-cmd: `test-e2e`
```


### 3. Kubebuilder Container Build and Release ([`kubebuilder-container-build-and-release.yaml`](.github/workflows/kubebuilder-container-build-and-release.yaml))

Builds container images for Kubebuilder projects with semantic versioning and optional release creation.

**Usage:**
```yaml
jobs:
  build-and-release:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-container-build-and-release.yaml@v1
    secrets: inherit
    with:
      push: true                 # Optional: Push image (default: true)
      release: true              # Optional: Create release (default: true)
      image-name: "my-operator"  # Optional: Image name (defaults to repository name)
      registry: "ghcr.io"        # Optional: Registry (default: ghcr.io)
      dockerfile: "Dockerfile"   # Optional: Dockerfile path
      context: "."               # Optional: Build context
    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
```

### 4. Go Module Release ([`go-module-release.yaml`](./.github/workflows/go-module-release.yaml))

Creates GitHub Releases for Go modules without container building.

**Usage:**
```yaml
jobs:
  release:
    uses: konfidence-project/.github/.github/workflows/go-module-release.yaml@v1
    secrets: inherit
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write
```

## Available Actions

Following GitHub Actions are used inside the shared Workflows and could also be used seperately:

- **[GitHub Repo Access](.github/actions/github-repo-access/action.yaml)**: Sets up GitHub CLI authentication for accessing private repositories within the organization.
- **[Setup Go](.github/actions/setup-go/action.yaml)**: Configures Go with access to the konfidence-project GitHub org and sets the GOPRIVATE environment variable for subsequent workflows.
- **[Kubebuilder Docker Build](.github/actions/kubebuilder-docker-build/action.yaml)**: Builds and optionally pushes Kubebuilder container images with proper manifests generation.
- **[Semantic Release](./.github/actions/semantic-release/action.yaml)**: Executes semantic release with automatic configuration detection and conventional commits. Semantic release will also create the GitHub release.


## Integration Examples

### CI Workflow (No Push/Release)

For pull requests and non-main branches:

```yaml
# .github/workflows/ci.yaml
name: Kubebuilder CI
on: 
  push:
    branches-ignore:
      - main # For commit on main branches, the release workflow will run
  pull_request:
    branches:
      - main

jobs:
  lint:
    name: Lint
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
    secrets: inherit

  test:
    name: Test
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: true
      install-crds: true
      crds-version: v0.0.1 

  build-and-release:
    name: Build Container Image
    if: github.event_name == 'pull_request'
    uses: konfidence-project/.github/.github/workflows/kubebuilder-container-build-and-release.yaml@v1
    secrets: inherit
    with: 
      push: false  # Don't push the built container image in CI 

    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
```

### Release Workflow (Push & Release)

For main branch deployments:

```yaml
# .github/workflows/release.yaml
name: Release

on:
  push: 
    branches: [main]

jobs:
  lint:
    name: Lint
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
    secrets: inherit

  test:
    name: Test
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: true
      install-crds: true
      crds-version: 6f560b268fa798ee96457551578fe84e90ae2acf
  build-and-release:
    needs:
      - lint
      - test
    name: Build and Release Container Image
    uses: konfidence-project/.github/.github/workflows/kubebuilder-container-build-and-release.yaml@v1
    secrets: inherit
    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
```

**Key Differences:**
- **CI Workflow**: Jobs run in parallel, `push: false` to avoid pushing artifacts, no release creation
- **Release Workflow**: Jobs run sequentially with dependencies, full push and release enabled

## Usage

### Secrets Requirement
All jobs using these shared workflows require `secrets: inherit` to access the organization secret for private repository access.

### Versioning of workflows
Use major version tags (e.g., `@v1`) which are automatically updated to point to the latest release. Updates are only needed when breaking changes are introduced.

```yaml
# ✅ Recommended: Always gets latest v1.x.x
uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
```

> The release of the shared GitHub Workflows is configured within the [`release-workflow-version`](.github/workflows/release-workflow-version.yaml) workflow.

> When fetching new changes with git using `git fetch` you may encounter following error: `! [rejected]        v1         -> v1  (would clobber existing tag)`. You can run  `git fetch -Pf` to force update the tag.

## Semantic Release Configuration

This repository uses [semantic-release](https://semantic-release.gitbook.io/) with conventional commits:

### Commit Types and Release Impact

| Commit Type | Release Type | Example |
|-------------|--------------|---------|
| `feat:` | Minor | `feat: add new workflow parameter` |
| `fix:` | Patch | `fix: resolve authentication issue` |
| `perf:` | Patch | `perf: optimize build performance` |
| `build:` | Patch | `build: update dependencies` |
| `ci:` | Patch | `ci: improve workflow reliability` |
| `docs:` | Patch | `docs: update README` |
| `style:` | Patch | `style: format YAML files` |
| `refactor:` | Patch | `refactor: restructure action` |
| `chore:` | Patch | `chore: update config` |
| `BREAKING CHANGE:` | Major | Any commit with breaking change footer |

## Renovate Configuration

The repository includes Renovate configuration presets for dependency management:

### Using the Base Preset

Add to your repository's `renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "github>konfidence-project/.github//renovate-config/presets/base.json5"
  ]
}
```

### Features Included

- **Auto-merge**: Patch updates and digests are automatically merged
- **Semantic commits**: All updates use conventional commit format
- **Smart grouping**: Related updates are grouped together
- **Security focused**: Vulnerability updates are prioritized

