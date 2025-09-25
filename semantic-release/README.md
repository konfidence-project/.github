# Semantic Release Configuration

This repository uses [semantic-release](https://semantic-release.gitbook.io/) with conventional commits for automated versioning and release management.

## Commit Types and Release Impact

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

## How It Works

1. **Conventional Commits**: All commits should follow the [conventional commits](https://www.conventionalcommits.org/) specification
2. **Automatic Versioning**: Based on commit types, semantic-release automatically determines the next version
3. **Release Creation**: Creates GitHub releases with generated changelogs
4. **Tag Management**: Manages Git tags and updates major version tags (e.g., `v1` always points to latest `v1.x.x`)

## Configuration Files

The semantic-release configuration is located in this directory and includes:
- Default release configuration
- Custom plugins setup
- Changelog generation rules