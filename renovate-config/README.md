# Renovate Configuration

Renovate configuration presets for automated dependency management across Konfidence Project repositories.

## Using the Base Preset

Add to your repository's `renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "github>konfidence-project/.github//renovate-config/presets/base.json5"
  ]
}
```

## Features Included

### Auto-merge
- Patch updates and digests are automatically merged
- Security updates are prioritized
- Non-breaking updates are handled automatically

### Semantic Commits
- All updates use conventional commit format
- Commit messages follow the pattern: `fix(deps): update dependency X to vY`
- Enables proper semantic versioning in release workflows

### Smart Grouping
- Related updates are grouped together
- Reduces PR noise
- Logical grouping by package ecosystem

### Security Focused
- Vulnerability updates are prioritized
- Security patches are fast-tracked
- Critical updates get immediate attention

## Preset Structure

The configuration is organized into presets for different purposes:

- **base.json5**: Main preset with all standard configurations
- Additional presets can be added for specific use cases

## Customization

You can extend or override the base preset in your repository:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "github>konfidence-project/.github//renovate-config/presets/base.json5"
  ],
  "schedule": ["after 10pm every weekday"],
  "timezone": "Europe/Berlin"
}
```

## Common Overrides

### Disable Auto-merge
```json
{
  "packageRules": [
    {
      "matchPackagePatterns": ["*"],
      "automerge": false
    }
  ]
}
```

### Add Custom Schedule
```json
{
  "schedule": ["before 3am on Monday"]
}
```

### Group Specific Dependencies
```json
{
  "packageRules": [
    {
      "matchPackageNames": ["@types/node", "typescript"],
      "groupName": "typescript dependencies"
    }
  ]
}
```