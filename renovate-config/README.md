# Renovate Configuration

This includes Renovate configuration presets for dependency management:

## Using the Base Preset

Add to your project's `renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "github>konfidence-project/.github//renovate-config/presets/base.json5"
  ]
}
```

## Features Included

- **Auto-merge**: Patch updates and digests are automatically merged
- **Semantic commits**: All updates use conventional commit format
- **Smart grouping**: Related updates are grouped together
- **Security focused**: Vulnerability updates are prioritized

## Preset Structure

The configuration is organized into presets for different purposes:

- **base.json5**: Main preset with all standard configurations
- Additional presets can be added for specific use cases

## Customization

You can extend or override the base preset in your project:

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