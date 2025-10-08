# Semantic Release Configuration

This configuration uses [semantic-release](https://semantic-release.gitbook.io/) with conventional commits for automated versioning and release management.

## Commit Types and Release Impact

| Commit Type | Release Type | Visible in Release Notes | Example |
|-------------|--------------|-------------------------|---------|
| `feat:` | Minor | ✅ Yes (Features) | `feat: add new workflow parameter` |
| `fix:` | Patch | ✅ Yes (Bug Fixes) | `fix: resolve authentication issue` |
| `perf:` | Patch | ✅ Yes (Performance Improvements) | `perf: optimize build performance` |
| `chore(deps):` | Patch | ✅ Yes (Maintenance) | `chore(deps): update dependencies` |
| `chore(security):` | Patch | ✅ Yes (Maintenance) | `chore(security): patch vulnerability` |
| `chore:` | No release | ✅ Yes (Maintenance) | `chore: update config` |
| `docs:` | No release | ❌ No (hidden) | `docs: update README` |
| `style:` | No release | ❌ No (hidden) | `style: format YAML files` |
| `refactor:` | No release | ❌ No (hidden) | `refactor: restructure action` |
| `build:` | No release | ❌ No (hidden) | `build: update build config` |
| `ci:` | No release | ❌ No (hidden) | `ci: improve workflow reliability` |
| `BREAKING CHANGE:` | Major | ✅ Yes | Any commit with breaking change footer |

> **Note**: Only `chore` commits with scope `deps` or `security` trigger a patch release. Other `chore` commits without these scopes will not trigger a release but will appear in the release notes if included in a release.

## How It Works

1. **Conventional Commits**: All commits should follow the [conventional commits](https://www.conventionalcommits.org/) specification
2. **Automatic Versioning**: Based on commit types, semantic-release automatically determines the next version
3. **Release Creation**: Creates GitHub releases with generated changelogs
4. **Tag Management**: Manages Git tags and updates major version tags (e.g., `v1` always points to latest `v1.x.x`)

## Configuration Files

The semantic-release configuration includes:
- Default release configuration
- Custom plugins setup
- Changelog generation rules