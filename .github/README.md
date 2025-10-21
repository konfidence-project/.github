# GitHub Actions Workflows and Actions for Konfidence Project

This .github directory inside the .github repository contains shared files and configurations for the Konfidence Project GitHub organization, including:

- **GitHub Workflows**: Reusable CI/CD workflows for Go projects and Kubebuilder operators
- **GitHub Actions**: Composite actions for common tasks like authentication and building
- **Semantic Release Configuration**: Standardized release automation with conventional commits
- **Renovate Configuration**: Dependency management presets for automated updates
- **Organization Templates**: Pull request templates and other GitHub organization files

## Available Workflows

### Composite Pipeline Workflows (v2+)

**New in v2:** Composite workflows that orchestrate multiple atomic workflows for cleaner integration of kubebuilder repos.

#### Kubebuilder CI Pipeline ([`kubebuilder-ci-pipeline.yaml`](./workflows/kubebuilder-ci-pipeline.yaml))

Orchestrates linting, testing, and building for CI scenarios (PRs and non-main branches).

**What it does:**
- Runs Go linting via `golang-lint.yaml`
- Runs tests via `kubebuilder-test.yaml`
- Builds multi-platform container images (no push/release)

**Usage:**
```yaml
# .github/workflows/ci.yaml
name: CI
on:
  pull_request:
  push:
    branches-ignore: [main]

jobs:
  ci:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-ci-pipeline.yaml@v3
    secrets: inherit
    with:
      before-tests: make generate-test-crds
```

**Inputs:**
- `before-tests`: Command to run before tests
- `image-name`: Container image name (default: `${{ github.repository }}`)
- `registry` (default: `ghcr.io`): Container registry
- All inputs from atomic workflows (dockerfile, context, bake-file, etc.)

#### Kubebuilder Release Pipeline ([`kubebuilder-release-pipeline.yaml`](./workflows/kubebuilder-release-pipeline.yaml))

Orchestrates linting, testing, building, and releasing for main branch deployments.

**What it does:**
- Calculates semantic version and image tags (single source of truth)
- Runs Go linting via `golang-lint.yaml`
- Runs tests via `kubebuilder-test.yaml`
- Builds multi-platform images and creates GitHub releases

**Usage:**
```yaml
# .github/workflows/release.yaml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-release-pipeline.yaml@v3
    secrets: inherit
    with:
      before-tests: make generate-test-crds
    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
```

**Key Features:**
- **Image Tag Calculation:** Generates the image tag which is used for docker build and kustomize
- **Semantic Version Dry-Run:** Determines next version before building
- **Parallel Execution:** Lint and test run concurrently after version calculation

**Outputs:**
- `metadata`: Build metadata from Docker
- `version`: Semantic version created
- `image-tag`: Full container image tag
- `image-digest`: Container image digest

---

### Atomic Workflows

These workflows handle specific tasks and can be used individually or via pipeline workflows.

### 1. Golang Lint ([`golang-lint.yaml`](./workflows/golang-lint.yaml))

Runs golangci-lint on Go projects with private repository access.

**Inputs:** None (uses repository's `.golangci.yml`)

**Usage:**
```yaml
jobs:
  lint:
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v3
    secrets: inherit
```

### 2. Kubebuilder Test ([`kubebuilder-test.yaml`](./workflows/kubebuilder-test.yaml))

Testing workflow for Kubebuilder projects with optional Kind cluster and CRD installation.

**Inputs:**
- `test-cmd` (default: `test`): Make target to run
- `before-tests`: Command to run before tests
- `after-tests`: Command to run after tests

**Usage:**
```yaml
jobs:
  test:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-test.yaml@v3
    secrets: inherit
    with:
      test-cmd: "test"
```

### 3. Kubebuilder Build and Release ([`kubebuilder-build-and-release.yaml`](./workflows/kubebuilder-build-and-release.yaml))

Builds multi-platform container images with semantic versioning and GitHub release creation.

**Inputs:**
- `push` (default: `true`): Push image to registry
- `release` (default: `true`): Create GitHub release
- `image-name`: Custom image name (defaults to repository name)
- `registry` (default: `ghcr.io`): Container registry
- `dockerfile` (default: `Dockerfile`): Path to Dockerfile
- `context` (default: `.`): Build context
- `bake-file` (default: `docker-bake.hcl`): Path to docker-bake configuration
- `targets`: Bake targets to build (comma-separated, empty = all)
- `platforms` (default: `linux/amd64,linux/arm64`): Target platforms
- `release_manifests` (default: `true`): Generate k8s manifests as release assets

**Outputs:**
- `new-release-published`: `true`/`false`
- `new-release-version`: Release version
- `metadata`: Docker build metadata

**Usage:**
```yaml
jobs:
  build-and-release:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-build-and-release.yaml@v3
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
    uses: konfidence-project/.github/.github/workflows/go-module-release.yaml@v3
    secrets: inherit
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write
```

## Multi-Platform Build Requirements (v2+)

All Kubebuilder projects must support multi-platform builds using BuildKit secrets and docker-bake.

### Dockerfile Requirements

Currently, the Dockerfiles use a BuildKit secret to be able to pull the private Go modules.

#### Example Dockerfile

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24-alpine AS builder
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

WORKDIR /workspace

RUN apk add --no-cache git ca-certificates

COPY go.mod go.sum ./

ENV GOPRIVATE=github.com/konfidence-project/*
RUN --mount=type=secret,id=gh_token \
    GH_TOKEN=$(cat /run/secrets/gh_token) && \
    git config --global url."https://x-access-token:${GH_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    go mod download && \
    git config --global --unset url."https://x-access-token:${GH_TOKEN}@github.com/".insteadOf

COPY cmd/ cmd/
COPY internal/ internal/

RUN CGO_ENABLED=0 GOOS=${TARGETOS:-linux} GOARCH=${TARGETARCH} \
    go build -a -o manager cmd/main.go

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532

ENTRYPOINT ["/manager"]
```

**Key points:**
- `--mount=type=secret,id=gh_token`: Mounts secret at build time only
- Token is read from `/run/secrets/gh_token` and never stored in layers
- `git config --unset`: Cleans up git configuration after use
- Multi-platform args (`TARGETOS`, `TARGETARCH`) enable cross-compilation


### docker-bake.hcl Configuration

All projects must include a `docker-bake.hcl` file for multi-platform builds:

```hcl
variable "TAG" {
  default = "dev"
}

variable "REGISTRY" {
  default = "ghcr.io/konfidence-project"
}

group "default" {
  targets = ["my-operator"]
}

target "my-operator" {
  context    = "."
  dockerfile = "Dockerfile"
  platforms  = ["linux/amd64", "linux/arm64"]
  tags       = ["${REGISTRY}/my-operator:${TAG}"]
  
  # Maps GH_TOKEN environment variable to gh_token secret
  secret = ["id=gh_token,env=GH_TOKEN"]
}
```

**Configuration explained:**
- `platforms`: Defines target architectures
- `secret`: Maps environment variable to BuildKit secret ID
- `tags`: Image tags (can use variables for dynamic values)

### Local Development

Building locally with multi-platform support:

```bash
# Set GitHub token
export GH_TOKEN="ghp_your_token_here"

# Build for all platforms
docker buildx bake

# Build for specific platform
docker buildx bake --set *.platform=linux/amd64 --load

# Build with custom tag
docker buildx bake --set *.tags=my-operator:test --load
```

> You can print out a GitHub token with `gh auth token`.


## Available Actions

### 1. GitHub Repo Access ([`github-repo-access`](./actions/github-repo-access/action.yaml))

Authenticates GitHub CLI for private repository access using GitHub App.

**Inputs:**
- `private-key` (required): GitHub App private key

**Usage:**
```yaml
- uses: konfidence-project/.github/.github/actions/github-repo-access@v3
  with:
    private-key: ${{ secrets.KONFIDENCE_PROJECT_REPO_ACCESS_PRIVATE_KEY }}
```

### 2. Setup Go ([`setup-go`](./actions/setup-go/action.yaml))

Configures Go with `GOPRIVATE` for konfidence-project repositories.

**Inputs:**
- `go-version-file` (default: `go.mod`): Path to go.mod

**Usage:**
```yaml
- uses: konfidence-project/.github/.github/actions/setup-go@v3
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
- uses: konfidence-project/.github/.github/actions/kubebuilder-docker-build@v3
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
  uses: konfidence-project/.github/.github/actions/semantic-release@v3
  with:
    dry-run: false
```

**Note:** Requires `GH_TOKEN` environment variable (set by `github-repo-access` action).


## Integration Examples

### Recommended: Pipeline Workflows

#### CI Workflow (Pull Requests)

```yaml
# .github/workflows/ci.yaml
name: CI
on:
  pull_request:
  push:
    branches-ignore: [main]

jobs:
  ci:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-ci-pipeline.yaml@v3
    secrets: inherit
    permissions:
      contents: read
      packages: read
      attestations: write
      id-token: write
    with:
      before-tests: make generate-test-crds
```

#### Release Workflow (Main Branch)

```yaml
# .github/workflows/release.yaml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    uses: konfidence-project/.github/.github/workflows/kubebuilder-release-pipeline.yaml@v3
    secrets: inherit
    permissions:
      contents: write
      issues: write
      pull-requests: write
      packages: write
      attestations: write
      id-token: write
    with:
      before-tests: make generate-test-crds
```

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
Use major version tags (e.g., `@v3`) which are automatically updated to point to the latest release. Updates are only needed when breaking changes are introduced.

```yaml
# ✅ Recommended: Always gets latest v2.x.x
uses: konfidence-project/.github/.github/workflows/kubebuilder-ci-pipeline.yaml@v3

# ❌ Not recommended: Pinned to specific version, misses updates
uses: konfidence-project/.github/.github/workflows/kubebuilder-ci-pipeline.yaml@v3.0.1

# ⚠️ Use with caution: Always uses latest, may include breaking changes
uses: konfidence-project/.github/.github/workflows/kubebuilder-ci-pipeline.yaml@main
```

**Version History:**
- **v2.x**: Multi-platform builds, BuildKit secrets, pipeline workflows
- **v1.x**: Single-platform builds, individual workflows only

**Version Tag Management:**
- The release of the shared GitHub Workflows is configured within the [`release-workflow-version`](./workflows/release-workflow-version.yaml) workflow
- When a new release is created, the major version tag (e.g., `v3`) is automatically updated to point to the latest release
- This ensures all repositories using `@v3` automatically get the latest non-breaking updates

**Git Fetch Note:**
> When fetching new changes with git using `git fetch` you may encounter following error: `! [rejected]        v1         -> v1  (would clobber existing tag)`. You can run  `git fetch -Pf` to force update the tag.

## Troubleshooting

### Private Module Access
**Problem:** `go: module ... not found`

**Solution:** Ensure `secrets: inherit` is set and organization secret `KONFIDENCE_PROJECT_REPO_ACCESS_PRIVATE_KEY` is configured.

### No Release Created
**Problem:** Workflow runs but no release

**Solution:** Ensure commits follow [Conventional Commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, etc.) and workflow runs on `main` branch.

### Image Push Failures
**Problem:** Build succeeds but push fails

**Solution:** Verify `packages: write` permission is set in workflow.
