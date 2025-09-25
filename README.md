# Konfidence Project - Shared GitHub Organization Files

This repository contains shared files and configurations for the Konfidence Project GitHub organization.

## 📁 Repository Structure

### [GitHub Workflows](.github/workflows/)
Reusable CI/CD workflows for Go projects and Kubebuilder operators. Includes workflows for linting, testing, building, and releasing.

- **Golang Lint** - Code quality checks for Go projects
- **Kubebuilder Test** - Comprehensive testing with Kind cluster support
- **Container Build & Release** - Multi-arch container builds with semantic versioning
- **Go Module Release** - Automated releases for Go modules

[→ Learn more about workflows](.github/workflows/README.md)

### [GitHub Actions](.github/actions/)
Composite actions for common tasks that can be used within workflows:

- **GitHub Repo Access** - Authentication for private repositories
- **Setup Go** - Go environment configuration with private module support
- **Kubebuilder Docker Build** - Container image building and manifest generation
- **Semantic Release** - Automated versioning and release creation

[→ Learn more about actions](.github/actions/README.md)

### [Semantic Release Configuration](./semantic-release/)
Standardized release automation using conventional commits. Automatically determines version numbers, creates releases, and manages tags.

[→ Learn more about semantic release](./semantic-release/README.md)

### [Renovate Configuration](./renovate-config/)
Dependency management presets for automated updates. Features auto-merge for patches, smart grouping, and security-focused updates.

[→ Learn more about Renovate config](./renovate-config/README.md)

### [Organization Templates](./profile/)
Default community health files and templates for the organization.

## 🚀 Quick Start

### Using Reusable Workflows

Add to your workflow file:

```yaml
jobs:
  lint:
    uses: konfidence-project/.github/.github/workflows/golang-lint.yaml@v1
    secrets: inherit
```

### Using Renovate Preset

Add to your `renovate.json`:

```json
{
  "extends": [
    "github>konfidence-project/.github//renovate-config/presets/base.json5"
  ]
}
```

## 📋 Requirements

- All workflows require `secrets: inherit` for organization secret access
- The `KONFIDENCE_GITHUB_TOKEN` organization secret must be configured
- Use versioned references (e.g., `@v1`) for stability

## 📖 Documentation

For detailed documentation on each component, please refer to the README files in the respective directories:

- [Workflows Documentation](.github/workflows/README.md)
- [Actions Documentation](.github/actions/README.md)
- [Semantic Release Documentation](./semantic-release/README.md)
- [Renovate Configuration Documentation](./renovate-config/README.md)

## 🔄 Version Management

We use semantic versioning with major version tags:
- `@v1` - Always points to the latest v1.x.x release
- Updates within the same major version are backward compatible
- Breaking changes trigger a new major version

## 📝 License

See [LICENSE](./LICENSE) for details.

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.