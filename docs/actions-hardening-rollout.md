# Actions hardening rollout

Baseline: [NeoNephos Actions hardening guide](https://github.com/neonephos/account-administration/blob/main/docs/actions-hardening-guide.md).

## Merge prerequisites — organization/repository owners

These changes are not a substitute for server-side controls. Before merging the
release workflow migration in each caller repository:

- Create a `release` environment, require independent maintainer reviewers,
  prevent self-review, disallow administrator bypass where possible, and allow
  only protected `main` and protected release tags. Move release App credentials
  into environment secrets. Do not leave an automatically created, unprotected
  environment as the final configuration.
- Protect the **actual** release tag names. The consumers use unprefixed
  `X.Y.Z[-suffix]`; a rule matching only `v*` does not protect those releases.
  Protect moving major workflow tags too. Restrict App bypass rights.
- Require code-owner reviews, dismiss stale approvals, and require approval of
  the latest push. CODEOWNERS does not activate that requirement by itself.
- Set the default token to read-only; disable Actions-created/approved PRs.
  Automation that opens release PRs uses a downscoped GitHub App token instead.
- Require approval for **all** external fork contributors. Select GitHub-owned,
  verified, and explicitly allowlisted actions; enforce full SHA pins.
- Restrict self-hosted/larger runner groups to selected protected workflows and
  repositories; disallow public/fork PR access. The workflows here no longer
  require custom runners for PR builds.
- Disable Actions on archived/mirror repositories. Review runner/secret
  inventories, remove unused entries and rotate credentials previously made
  available to PR code. Review external OIDC/token service trust separately.

## Workflow interface migration

- Pin reusable workflows to the reviewed hardening commit, not `main` or `v4`.
  Merge the shared workflow PR before its consumers (retain the pinned commits;
  do not squash away commits referenced by consumers).
- PR lint/test/build callers use `goreleaser-pr.yaml` with `contents: read`, no
  inherited secrets, no package/attestation/OIDC write grants, and standard
  GitHub-hosted runners. Publishing uses a separate call to `goreleaser.yaml`
  after checks pass, on trusted push events, with contents/packages write only.
- `github-app-auth` now returns `outputs.token`; it no longer writes `GH_TOKEN`
  into the job environment or installs a persistent Git credential helper.
  Pass the token only to the consuming step. Specify permission inputs explicitly.
- Only release/prerelease/secret-review calls pass the single App private key.
  Do not use `secrets: inherit`. The release environment must gate release keys.
- Arbitrary shell hooks in controller tests are removed. `before-tests` accepts
  only an empty string or `pnpm install --frozen-lockfile`; Make target inputs
  are validated and passed as arguments. `after-tests` must be empty.
- Dependabot automation queues eligible non-Actions updates for auto-merge but
  **never approves them** and never uses a bypass-capable App. Required human
  approvals and checks must still be configured. Actions updates need review.

## Validation and limitations

Use actionlint and `zizmor --offline --no-config --no-ignores .github`.
The workflow-security job blocks high-confidence, high-severity findings; review
all remaining findings manually. Metadata-only `pull_request_target` workflows
are intentional: they do not check out or execute PR code.

Offline scans do not verify external service policy, artifact/binary provenance,
runner isolation, or repository settings. SHA pinning prevents a later ref move;
it does not establish that the pinned dependency was safe when selected. Review
Dependabot pin updates rather than auto-approving them.
