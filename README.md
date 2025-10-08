# Konfidence Project - Shared GitHub Organization Files

This documentation covers shared files and configurations for the Konfidence Project GitHub organization.

## Available Components

### [GitHub Workflows](.github/workflows/)
Reusable CI/CD workflows for Go projects and Kubebuilder operators. Includes workflows for linting, testing, building, and releasing.

- **Golang Lint** - Code quality checks for Go projects
- **Kubebuilder Test** - Comprehensive testing with Kind cluster support
- **Container Build & Release** - Multi-arch container builds with semantic versioning
- **Go Module Release** - Automated releases for Go modules


### [GitHub Actions](.github/actions/)
Composite actions for common tasks that can be used within workflows:

- **GitHub Repo Access** - Authentication for private repositories
- **Setup Go** - Go environment configuration with private module support
- **Kubebuilder Docker Build** - Container image building and manifest generation
- **Semantic Release** - Automated versioning and release creation

[→ Detailed workflows and actions documentation](.github/README.md)

### [Semantic Release Configuration](./semantic-release/)
Standardized release automation using conventional commits. Automatically determines version numbers, creates releases, and manages tags.

[→ Semantic release documentation](./semantic-release/README.md)

### [Renovate Configuration](./renovate-config/)
Dependency management presets for automated updates. Features auto-merge for patches, smart grouping, and security-focused updates.

[→ Renovate configuration documentation](./renovate-config/README.md)

### [Organization Templates](./profile/)
Default community health files and templates for the organization.

## 🚀 Quick Start

### Using Reusable Workflows

To use in your project, add to your workflow file:

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

- These workflows require `secrets: inherit` for organization secret access
- The `KONFIDENCE_GITHUB_TOKEN` organization secret must be configured
- Use versioned references (e.g., `@v1`) for stability

## 📖 Additional Resources

For detailed documentation on each component, please refer to the documentation in the respective directories:

- [Workflows/ Actions Documentation](.github/README.md)
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