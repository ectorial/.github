# ectorial delivery overview

[WSR ROADMAP.md](https://github.com/ectorial/wsr/blob/main/ROADMAP.md) owns delivery order and gates.
This file is a summary, not a separate version schedule.

## Current scaffold

WSR has argument parsing, shared types, and workspace/CI definitions. Workflow inspection, execution,
and isolation are not implemented in its current checkout. Local prototype code remains stashed.
The organization profile/template summarize the same product direction and implementation status.

## Next — planned

- Reconcile preserved prototype evidence with accepted design and open questions.
- Specify and test compatibility inspection/planning without executing workload code.
- Prove component capability enforcement and isolated Linux system execution.
- Deliver useful local execution with explicit state, permissions, and results.
- Reuse the same engine inside GitHub Actions after defining its wrapper contract.

Independent CI, catalogs, more providers, remote cache, and native macOS/Windows jobs are later
possibilities. No action components, registry, or measured startup/compatibility guarantee is available.

Repository removals are complete: `actions`, `.github-private`, and `demo-repository` were deleted
on October 7, 2026. Do not recreate them merely to fill architecture boxes.
