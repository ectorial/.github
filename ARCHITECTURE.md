# ectorial organization architecture

## Repository ownership

The retained product repositories are `ectorial/wsr` and `ectorial/.github`.
WSR owns workflow compilation, planning, execution, security contracts, and technical decisions.
This repository owns organization presentation and governance. It does not host the workflow engine.
The legacy Node profile generator is unrelated to a future GitHub App/controller.

`actions`, `.github-private`, and `demo-repository` were deleted on October 7, 2026.
No catalog, registry, SDK, or separate orchestration repository is required by the current milestone.
References to those repositories in [historical drafts](docs/archive/2026-06/README.md) are historical.

## Product architecture — summary only

WSR's current code is a CLI/workspace scaffold; its command handlers are not implemented.
A local stash preserves prototype work that is absent from the checkout and not a supported release.

The accepted direction is independent local CI with optional hosted reuse and reporting. Component Model execution
is central to deny-by-default security; isolated Linux system execution handles existing tools.
Linux jobs from macOS/Linux machines come first. Malicious workloads are assumed. Broad runner access
is an explicit owner-authorized exception with scope and syntax still open.

Bun is the intended runtime for compatible GHA JavaScript actions inside system isolation; this is
a planned compatibility path, not implemented support or a new security boundary. The provider
adapter and provider-neutral core remain. [The GHA crate design](https://github.com/ectorial/wsr/tree/main/crates/wsr-gha)
owns compatibility details and validation gaps under WSR decision D-024.

Provisioning/cache, scheduling/dispatch, enforcement, observability and evidence have separate
owning WSR guides. Remote CI hosting is a later possibility. The component runtime, Bun version/provisioning, outer isolation,
CPU architectures, wrapper semantics, and compatibility coverage remain open.

The authoritative records are [WSR architecture](https://github.com/ectorial/wsr/blob/main/ARCHITECTURE.md)
and [WSR decisions](https://github.com/ectorial/wsr/blob/main/PLAN.md). Update those before changing this summary.
