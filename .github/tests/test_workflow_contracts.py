"""Dependency-free regression tests for security-sensitive workflow contracts.

Only the isolated validation shell snippets execute. No checkout, package install,
App authentication, tag push, build, publication or deployment is performed.
"""
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest

WORKFLOWS = Path(__file__).resolve().parents[1] / "workflows"


def source(filename):
    return (WORKFLOWS / filename).read_text()


def shell_step(filename, name):
    lines = source(filename).splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "- name: " + name)
    run = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "run: |")
    indent = len(lines[run]) - len(lines[run].lstrip())
    end = run + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        end += 1
    return textwrap.dedent("\n".join(lines[run + 1:end]))


def execute(script, **env):
    with tempfile.TemporaryDirectory() as cwd:
        return subprocess.run(
            ["/bin/bash", "-e", "-o", "pipefail", "-c", script],
            cwd=cwd,
            env={"PATH": "/usr/bin:/bin", **env},
            text=True,
            capture_output=True,
            check=False,
        )


class WorkflowContracts(unittest.TestCase):
    def test_publish_event_mode_and_ref_matrix(self):
        script = shell_step("goreleaser.yaml", "Reject unsupported modes and untrusted events")
        for mode in ["main", "release", "pr", "unknown", "$(exit 0)"]:
            for event in ["push", "pull_request", "pull_request_target", "workflow_dispatch"]:
                for ref in ["refs/heads/main", "refs/heads/topic", "refs/tags/1.2.3"]:
                    allowed = event == "push" and (
                        mode == "main" and ref == "refs/heads/main"
                        or mode == "release" and ref in ["refs/heads/main", "refs/tags/1.2.3"]
                    )
                    with self.subTest(mode=mode, event=event, ref=ref):
                        result = execute(script, MODE=mode, GITHUB_EVENT_NAME=event, GITHUB_REF=ref)
                        self.assertEqual(result.returncode == 0, allowed, result.stdout + result.stderr)
        self.assertIn("    needs: validate", source("goreleaser.yaml"))

    def test_breaking_release_never_moves_v4(self):
        script = shell_step("release-please-pipeline.yaml", "Require a new major for the breaking workflow API")
        for tag, allowed in [("v4.8.1", False), ("v3.9.0", False), ("v5.0.0", True),
                             ("v6.1.0", True), ("v5", False), ("v5.0.0; exit 0", False)]:
            with self.subTest(tag=tag):
                self.assertEqual(execute(script, TAG=tag).returncode == 0, allowed)

    def test_pr_builder_is_read_only_and_versions_snapshots(self):
        text = source("goreleaser-pr.yaml")
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn(": write", text)
        self.assertNotIn("secrets.", text)
        self.assertIn("args: build --clean --single-target --snapshot", text)
        self.assertIn("GORELEASER_CURRENT_TAG: ${{ github.sha }}", text)
        self.assertIn("cache-binary: false", text)

    def test_no_branch_only_self_dependencies_or_mutable_uses(self):
        pattern = re.compile(r"^[ \t]*(?:-[ \t]*)?uses:[ \t]+([^ \t#\r\n]+)", re.MULTILINE)
        for path in WORKFLOWS.glob("*.yaml"):
            text = path.read_text()
            self.assertNotIn("cashapp/activate-hermit", text, path.name)
            for ref in pattern.findall(text):
                with self.subTest(workflow=path.name, ref=ref):
                    self.assertFalse(ref.startswith("konfidence-project/.github/"))
                    self.assertTrue(ref.startswith("./") or re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref))

    def test_security_check_runs_without_path_filters(self):
        text = source("workflow-lint.yaml")
        self.assertNotIn("paths:", text)
        for event in ["workflow_call", "pull_request", "merge_group", "push", "schedule"]:
            self.assertRegex(text, r"(?m)^  " + event + r":$")

    def test_removed_inputs_are_not_silently_ignored(self):
        self.assertNotIn("after-tests", source("test.yaml"))
        self.assertNotRegex(source("goreleaser.yaml"), r"(?m)^      runner:")

    def test_release_validation_needs_no_persisted_git_credentials(self):
        text = source("validate-release-tag.yaml")
        self.assertIn("fetch-depth: 0", text)
        self.assertIn("persist-credentials: false", text)
        self.assertNotIn("git fetch", text)
        self.assertIn('git merge-base --is-ancestor "$GITHUB_SHA" origin/main', text)

    def test_app_tokens_are_explicitly_repository_scoped(self):
        for name in ["release-please.yaml", "release-please-pipeline.yaml",
                     "prerelease-pipeline.yaml", "secret-scanning-review.yaml"]:
            with self.subTest(workflow=name):
                text = source(name)
                self.assertIn("owner: ${{ github.repository_owner }}", text)
                self.assertIn("repositories: ${{ github.event.repository.name }}", text)
                self.assertIn("permission-contents:", text)


if __name__ == "__main__":
    unittest.main()
