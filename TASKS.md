# ectorial coordination tasks

## Current scope

Maintain consistent documentation across the retained `wsr` and `.github` repositories.
[WSR PLAN.md](https://github.com/ectorial/wsr/blob/main/PLAN.md) owns technical decisions;
[WSR ROADMAP.md](https://github.com/ectorial/wsr/blob/main/ROADMAP.md) owns implementation gates.
No runtime or package-version choice is approved by this task list.

## Remaining coordination

- Review local diffs and untracked documentation in both repositories before publication.
- Publish coordinated changes only when explicitly requested; check public links after publication.
- Decide whether to repair, replace, retain, or retire legacy profile automation before reactivation.
  The generator replacement bug and package metadata were not repaired by documentation changes.
- Resolve wildcard scope, system-backend isolation, runtimes/toolchains, and the first compatibility
  contract through WSR's decision record. Re-check runtime/MSRV evidence when a runtime is selected.
- If authorized, review the preserved WSR stash in isolation and report measured recovery results.
- Before a future release, re-check package ownership, public crate boundaries, installer/schema
  availability, CI, and publishing configuration. Do not run old prototype setup commands as current instructions.

## Completed repository lifecycle decisions

`actions`, `.github-private`, and `demo-repository` were deleted from GitHub and locally on October 7, 2026.
No lifecycle decision remains pending for those repositories. No new catalog repository is required now.

## Deferred

GitHub App creation, webhook hosting, remote workers, protected-branch enforcement, and independent
CI are later possibilities after local execution and Actions engine reuse. No account authentication
snapshot or service setup instructions are asserted current here.

The [June-era task list](docs/archive/2026-06/TASKS.md) is preserved as historical context only.
