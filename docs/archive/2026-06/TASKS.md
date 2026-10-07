> Historical unpublished draft, preserved during the October 7, 2026 documentation reconciliation.
> This is not current status, policy, or an executable migration plan. References and commands
> describe the original June-era context and may refer to deleted repositories or old paths.
> Use the active [organization overview](../../../README.md) and
> [WSR decision record](https://github.com/ectorial/wsr/blob/main/PLAN.md) instead.

# ectorial manual tasks

## Status

This file records migration steps that require account authentication, an
external service, or explicit approval before changing GitHub state. It is not a
general implementation backlog; implementation phases remain in
[`MIGRATION.md`](MIGRATION.md).

Last audited: 2026-06-27.

## Current authentication

`gh auth status` confirms an active `carlosferreyra` login. The current token has
`repo`, `workflow`, and `read:org` scopes, and the account is an active ectorial
organization administrator.

`gh` uses its stored token automatically. For a script that specifically reads
`GITHUB_TOKEN`, use:

```sh
export GITHUB_TOKEN="$(gh auth token)"
```

For a script that expects `GH_TOKEN`, use:

```sh
export GH_TOKEN="$(gh auth token)"
```

Do not print either variable, write it to a repository file, or add it to shell
history manually.

## Approval required now

### Choose the Wasmtime/MSRV policy

`wsr` currently declares Rust 1.85 because it follows the current
`carlosferreyra/rust-template` baseline. The current Wasmtime release is 46.0.1
and declares Rust 1.94; Wasmtime 45 requires Rust 1.93, while the newest audited
release that fits Rust 1.85 is the older Wasmtime 31 line.

Choose one before embedding the production component runtime:

- raise the `wsr` MSRV to 1.94 and track the current Wasmtime release line;
- keep MSRV 1.85 and accept a pinned older runtime with an explicit security and
  upgrade policy;
- keep the host/runtime in a separate crate or process with a newer MSRV while
  preserving 1.85 for portable core crates.

The recommended choice is to isolate the runtime behind a workspace crate and
allow that crate/product release to use Rust 1.94. A security boundary should
not remain on an old runtime solely to preserve an unrelated minimum compiler
version. This changes the template-derived MSRV contract and therefore requires
an explicit decision.

### Review and publish local migration changes

No commits or pushes were made automatically. The `.github` and `wsr` working
trees contain migration work mixed with pre-existing local changes. Review the
complete diffs before deciding commit boundaries.

```sh
git -C ~/Development/ectorial/.github status --short
git -C ~/Development/ectorial/.github diff
git -C ~/Development/ectorial/wsr status --short
git -C ~/Development/ectorial/wsr diff
```

After review, either commit and push manually or explicitly authorize an agent
to prepare commits and draft pull requests. Do not stage all repositories as one
undifferentiated change.

### Decide the legacy `.github` automation lifecycle

The `.github` repository still contains legacy Node.js `gh-auto` profile
generation code. It is unrelated to the planned CI/CD GitHub App adapter.

Choose one:

- retain and repair it as organization-profile-only automation;
- replace it with deterministic static profile maintenance;
- remove it and its workflow;
- move it to a separate maintenance repository.

This is an architecture and maintenance decision, not an authentication issue.
No removal has been performed.

### Decide `.github-private` lifecycle

The `ectorial/.github-private` repository is currently public despite its name
and contains only a README, license, and gitignore.

Choose one:

- make it private and use it for an actual private organization profile;
- keep it public and rename it;
- archive it;
- delete it.

Visibility changes, renames, archival, and deletion require explicit approval.
After approval they can be performed with `gh repo edit` or the repository
settings UI. Deletion additionally requires a token with `delete_repo` and must
not be performed as part of routine migration cleanup.

### Decide `demo-repository` lifecycle

`ectorial/demo-repository` is private and contains GitHub demonstration content
and two unrelated Actions workflows.

Choose one:

- retain it as an organization demo;
- use selected workflows only as copied, pinned `wsr` compatibility fixtures;
- archive it;
- delete it.

The product must not depend on mutable content in this repository.

## Required before the remote execution milestone

### Create the ectorial GitHub App

Do this only after the Phase 7 webhook receiver has a stable public URL and its
credential storage is defined.

GitHub App creation is an organization-setting action and is best completed
through:

<https://github.com/organizations/ectorial/settings/apps/new>

Initial minimum repository permissions are expected to be:

- Metadata: read;
- Contents: read;
- Checks: write;
- Pull requests: read, if pull request metadata is required.

Initial webhook subscriptions are expected to be:

- `push`;
- `pull_request`;
- `check_run` for reruns and requested actions.

Before saving the App, verify these values against the implemented adapter. Do
not grant Actions write, Contents write, Administration, Secrets, or Workflows
write unless a reviewed feature requires them.

Store the App private key and webhook secret in the selected external secret
manager. Record only secret references in configuration; never commit private
keys or webhook secrets.

If browser automation is requested for this setup, the agent must state the
exact settings page and intended mutation in chat before opening Chrome.

### Configure a public webhook endpoint

The GitHub App requires an HTTPS endpoint that:

- validates webhook signatures;
- persists delivery identifiers for idempotency;
- responds within GitHub's timeout;
- queues work rather than executing it in the request;
- supports credential rotation without downtime.

The hosting provider, domain, deployment environment, and secret manager remain
undefined. These require an infrastructure decision before App installation.

### Install the GitHub App on selected repositories

Install the new App only after webhook verification and duplicate-delivery tests
pass. Start with repository selection limited to `ectorial/wsr`; do not grant
organization-wide access initially.

The organization currently has a separate `claude` GitHub App installation.
That installation is not the ectorial CI/CD App and must not be reused as the
product credential.

## Required before protected-branch enforcement

### Add repository rulesets

`ectorial/wsr` currently has no repository rulesets and `main` is not protected.
Do not require a check until its final GitHub Check name is stable; otherwise the
repository can be left unmergeable.

After the external check is proven, approve and create a ruleset requiring:

- pull requests before merge;
- the stable ectorial check name;
- branch deletion and force-push restrictions;
- an explicit administrator bypass policy;
- any desired review count and conversation-resolution policy.

Inspect current state with:

```sh
gh api repos/ectorial/wsr/rulesets
gh api repos/ectorial/wsr/branches/main/protection
```

Creating or changing rulesets is a remote policy mutation and requires explicit
approval even though the authenticated account is an organization admin.

## Required before publishing releases

### Decide whether `wsr` will publish to crates.io

The repository has cargo-dist GitHub release automation, but crates.io
publishing policy is not yet decided. Before running the template's publishing
setup script:

- confirm which crates are public;
- confirm ownership of all crate names;
- confirm lockstep versioning;
- review package metadata and generated README behavior;
- decide whether pre-alpha releases should be published.

The setup script requires an explicit crates.io token and performs external
state changes. Run its dry-run first:

```sh
cd ~/Development/ectorial/wsr
export GITHUB_TOKEN="$(gh auth token)"
export CARGO_REGISTRY_TOKEN="<short-lived crates.io token>"
uv run scripts/setup-crates-io-publish.py --dry-run
```

Do not place `CARGO_REGISTRY_TOKEN` in a file. Executing without `--dry-run`
requires a separate explicit approval because crate-name reservation and trusted
publisher configuration are externally visible and may be irreversible.

### Create the `release` environment if trusted publishing is approved

`ectorial/wsr` currently has only a `github-pages` environment. After approving
the release design, an administrator can create the expected environment with:

```sh
export GITHUB_TOKEN="$(gh auth token)"
gh api --method PUT repos/ectorial/wsr/environments/release
```

Configure deployment protection and trusted publishing in GitHub/crates.io UI
after environment creation. Environment creation and policy changes require
explicit approval.

## No manual action currently required

- `cargo-xdist` already follows the current generated Rust template structure
  and remains outside the `wsr` product boundary.
- `actions` should remain a placeholder until the WIT world, component package,
  signing policy, and conformance harness exist. Do not scaffold components only
  to make the repository appear active.
- Chrome is not required for the current local inspection and scaffolding work.
