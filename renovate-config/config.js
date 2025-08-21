module.exports = {
    platform: 'github',
    repositories: ["konfidence-project/konfidence-docs"],
    autodiscover: true,
    // autodiscoverFilter: ['.*'],
    onboarding: true,
    onboardingConfig: {
        "$schema": "https://docs.renovatebot.com/renovate-schema.json",
        "extends": [
            "github>konfidence-project/.github//renovate-config/presets/base.json5"
        ]
    },
    hostRules: [
        // GitHub API repo-scoped (für z.B. changelogs & lookups)
        {
            matchHost: 'https://api.github.com/repos/konfidence-project',
            hostType: 'github',
            token: process.env.RENOVATE_TOKEN,
        },
        // Raw git fetches (vendir git, git-refs, etc.)
        {
            matchHost: 'https://github.com/konfidence-project',
            token: process.env.RENOVATE_TOKEN,
        },
    ]
};