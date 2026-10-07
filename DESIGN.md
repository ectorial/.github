# ectorial product design overview

This document summarizes accepted direction. It is not implemented behavior or an independent
technical specification. [WSR PLAN.md](https://github.com/ectorial/wsr/blob/main/PLAN.md) owns decisions.

## Accepted direction — planned

1. Run and debug a documented subset of GitHub Actions workflows locally.
2. Reuse the same engine inside GitHub Actions.
3. Consider independent CI later, retaining GitHub integration where useful.

Provider components compile source into a canonical workflow model with compatibility diagnostics.
The execution core handles planning/evaluation and job supervision without runtime provider callbacks.
The Component Model supplies explicit typed execution interfaces; the host/runtime must enforce grants.
Existing shell commands and tools use a separately isolated Linux backend that rejects execution
when required restrictions cannot be enforced.

The first release targets Linux jobs from macOS and Linux development machines. Workloads may be
malicious. Owner/admin policy authorizes capabilities; workflows cannot authorize themselves.
A broad runner-access profile/wildcard is explicitly opt-in and never an automatic permission fallback.

## Open choices

Wildcard scope/syntax/granularity, VM-versus-container outer isolation on Linux, concrete runtimes/WASI,
CPU architectures, images, shared-state contracts, initial GHA coverage, and the Actions wrapper contract
remain unresolved. Managed-runner-only wildcard scope and a VM boundary on developer machines are
proposals, not accepted requirements. Broad grants do not establish full workflow compatibility.

## Evidence and further reading

The current checkout is a scaffold. Prototype inspection/planning, snapshots, a development command
backend, and GitHub adapter work survive in a local stash; they are not current functionality.
See [WSR architecture](https://github.com/ectorial/wsr/blob/main/ARCHITECTURE.md),
[security model](https://github.com/ectorial/wsr/blob/main/docs/SECURITY-MODEL.md), and
[delivery gates](https://github.com/ectorial/wsr/blob/main/ROADMAP.md).

The [older unpublished design](docs/archive/2026-06/DESIGN.md) is preserved as historical context.
Its independent-CI-first sequence and fixed technology assumptions do not override the current decisions.
