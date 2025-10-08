# GitHub Actions Workflows and Actions for Konfidence Project

This .github directory inside the .github repository contains shared files and configurations for the Konfidence Project GitHub organization, including:

- **GitHub Workflows**: Reusable CI/CD workflows for Go projects and Kubebuilder operators
- **GitHub Actions**: Composite actions for common tasks like authentication and building
- **Semantic Release Configuration**: Standardized release automation with conventional commits
- **Renovate Configuration**: Dependency management presets for automated updates
- **Organization Templates**: Pull request templates and other GitHub organization files

## Available Workflows

### 1. Golang Lint ([`golang-lint.yaml`](./workflows/golang-lint.yaml))

Runs golangci-lint on Go projects with private repository access.

**Inputs:** None (uses repository's `.golangci.yml`)

**Usage:**
```yaml
jobs:
  lint:
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
    secrets: inherit
```

### 2. Kubebuilder Test ([`kubebuilder-test.yaml`](./workflows/kubebuilder-test.yaml))

Testing workflow for Kubebuilder projects with optional Kind cluster and CRD installation.

**Inputs:**
- `with-kind-cluster` (default: `true`): Create Kind cluster
- `install-crds` (default: `true`): Install CRDs from konfidence-project/crds
- `crds-version` (default: `main`): Git ref for CRDs (⚠️ use specific commit in production)
- `test-cmd` (default: `test`): Make target to run
- `before-tests`: Command to run before tests
- `after-tests`: Command to run after tests

**Usage:**
```yaml
jobs:
  test:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v1
    secrets: inherit
    with:
      with-kind-cluster: true
      install-crds: true
      crds-version: "e029cc3"  # Use specific commit
      test-cmd: "test"
```

**Examples:**
```yaml
# Unit tests (no cluster)
test-unit:
  with:
    with-kind-cluster: false
    install-crds: false

# E2E tests (with cluster)
test-e2e:
  with:
    with-kind-cluster: true
    crds-version: "e029cc3"
    test-cmd: "test-e2e"
```


### 3. Kubebuilder Container Build and Release ([`kubebuilder-container-build-and-release.yaml`](./workflows/kubebuilder-container-build-and-release.yaml))

Builds container images with semantic versioning and GitHub release creation.

**Inputs:**
- `push` (default: `true`): Push image to registry
- `release` (default: `true`): Create GitHub release
- `image-name`: Custom image name (defaults to repository name)
- `registry` (default: `ghcr.io`): Container registry
- `dockerfile` (default: `Dockerfile`): Path to Dockerfile
- `context` (default: `.`): Build context

**Outputs:**
- `new-release-published`: `true`/`false`
- `new-release-version`: Release version

**Usage:**
```yaml
jobs:
  build-and-release:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-container-build-and-release.yaml@v1
    secrets: inherit
    with:
      push: true
      release: true
      image-name: "my-operator"
    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
```

### 4. Go Module Release ([`go-module-release.yaml`](./workflows/go-module-release.yaml))

Creates GitHub releases for Go modules without container building (libraries, CLI tools).

**Inputs:** None

**Outputs:**
- `new-release-published`: `true`/`false`
- `new-release-version`: Release version

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

### 1. GitHub Repo Access ([`github-repo-access`](./actions/github-repo-access/action.yaml))

Authenticates GitHub CLI for private repository access using GitHub App.

**Inputs:**
- `private-key` (required): GitHub App private key

**Usage:**
```yaml
- uses: konfidence-project/.github/.github/actions/github-repo-access@v1
  with:
    private-key: ${{ secrets.KONFIDENCE_PROJECT_REPO_ACCESS_PRIVATE_KEY }}
```

### 2. Setup Go ([`setup-go`](./actions/setup-go/action.yaml))

Configures Go with `GOPRIVATE` for konfidence-project repositories.

**Inputs:**
- `go-version-file` (default: `go.mod`): Path to go.mod

**Usage:**
```yaml
- uses: konfidence-project/.github/.github/actions/setup-go@v1
```

### 3. Kubebuilder Docker Build ([`kubebuilder-docker-build`](./actions/kubebuilder-docker-build/action.yaml))

Builds Kubebuilder container images with manifests generation.

**Inputs:**
- `image-name` (required): Image name
- `version` (default: `latest`): Image tag
- `push` (default: `false`): Push to registry
- `registry` (default: `ghcr.io`): Container registry
- `dockerfile` (default: `Dockerfile`): Dockerfile path
- `context` (default: `.`): Build context
- `github-token` (required): GitHub token

**Outputs:**
- `image-digest`, `image-id`, `tags`, `metadata`

**Usage:**
```yaml
- uses: konfidence-project/.github/.github/actions/kubebuilder-docker-build@v1
  with:
    image-name: ghcr.io/konfidence-project/my-operator
    version: v1.0.0
    push: true
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Semantic Release ([`semantic-release`](./actions/semantic-release/action.yaml))

Executes semantic-release with shared configuration.

**Inputs:**
- `dry-run` (default: `false`): Dry-run mode

**Outputs:**
- `new-release-published`: `true`/`false`
- `new-release-version`: Release version

**Usage:**
```yaml
- id: release
  uses: konfidence-project/.github/.github/actions/semantic-release@v1
  with:
    dry-run: false
```

**Note:** Requires `GH_TOKEN` environment variable (set by `github-repo-access` action).


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

  build:
    name: Build Container Image
    if: github.event_name == 'pull_request'
    uses: konfidence-project/.github/.github/workflows/kubebuilder-container-build-and-release.yaml@v1
    secrets: inherit
    with:
      push: false  # Don't push the built container image in CI
      release: false  # Don't create releases in CI
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
      crds-version: "6f560b268fa798ee96457551578fe84e90ae2acf"

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
- **CI Workflow**: Jobs run in parallel, `push: false` and `release: false` to avoid pushing artifacts and creating releases
- **Release Workflow**: Jobs run sequentially with dependencies, full push and release enabled

## Organization Files

This repository also includes organization-wide templates and configurations that are automatically applied to all repositories in the konfidence-project organization.

### Issue Templates

- **[Default Issue Template](./ISSUE_TEMPLATE/default-issue-template.md)**: Standardized template with sections for description, prerequisites, required steps, and open questions

### In Solidarity Configuration

- **[in-solidarity.yml](./in-solidarity.yml)**: Configuration for the [In Solidarity](https://github.com/apps/in-solidarity) GitHub App that helps promote inclusive language in code and documentation

## Related Configurations

- **[Semantic Release Configuration](../semantic-release/README.md)**: Shared configuration for automated versioning and release management
- **[Renovate Configuration](../renovate-config/README.md)**: Presets for automated dependency management

## Usage

### Secrets Requirement
All jobs using these shared workflows require `secrets: inherit` to access the organization secret for private repository access.

**Required Organization Secret:**
- `KONFIDENCE_PROJECT_REPO_ACCESS_PRIVATE_KEY`: GitHub App private key for accessing private repositories

### Versioning of Workflows
Use major version tags (e.g., `@v1`) which are automatically updated to point to the latest release. Updates are only needed when breaking changes are introduced.

```yaml
# ✅ Recommended: Always gets latest v1.x.x
uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1

# ❌ Not recommended: Pinned to specific version, misses updates
uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1.2.3

# ⚠️ Use with caution: Always uses latest, may include breaking changes
uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@main
```

**Version Tag Management:**
- The release of the shared GitHub Workflows is configured within the [`release-workflow-version`](./workflows/release-workflow-version.yaml) workflow
- When a new release is created, the major version tag (e.g., `v1`) is automatically updated to point to the latest release
- This ensures all repositories using `@v1` automatically get the latest non-breaking updates

**Git Fetch Note:**
> When fetching new changes with git using `git fetch` you may encounter following error: `! [rejected]        v1         -> v1  (would clobber existing tag)`. You can run  `git fetch -Pf` to force update the tag.

## Troubleshooting

### Private Module Access
**Problem:** `go: module ... not found`

Ensure `secrets: inherit` is set and organization secret `KONFIDENCE_PROJECT_REPO_ACCESS_PRIVATE_KEY` is configured.

### Kind Cluster Issues
**Problem:** Tests fail with Kubernetes errors

Set `with-kind-cluster: true` and use specific `crds-version` commit hash instead of `main`.

### No Release Created
**Problem:** Workflow runs but no release

Ensure commits follow [Conventional Commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, etc.) and workflow runs on `main` branch.

### Image Push Failures
**Problem:** Build succeeds but push fails

Verify `packages: write` permission is set in workflow.

## Best Practices

1. **Use specific CRD versions:** `crds-version: "e029cc3"` instead of `"main"`
2. **Separate CI/Release workflows:** Use `push: false` and `release: false` in PR workflows
3. **Follow conventional commits:** `feat:`, `fix:`, `perf:` for automatic versioning
4. **Test before merging:** Run workflows in PRs before merging to main