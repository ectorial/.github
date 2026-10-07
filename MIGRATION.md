# ectorial documentation and project reconciliation

## Status

October 7, 2026: this reconciliation aligns documentation across `wsr` and `.github`.
It does not restore the stash, implement runtimes, enable automation, or recreate deleted repositories.
[WSR PLAN.md](https://github.com/ectorial/wsr/blob/main/PLAN.md)
remains an architecture interview; unresolved choices are recorded rather than guessed.

## Established baseline

- `wsr` is a CLI/workspace scaffold; all eight command handlers are unimplemented.
- Its local July 29 stash preserves substantial prototype work absent from the checkout.
  Original object: `daee0885832df55a9a872037d3ce6741b9e6e72a`.
- The older migration reported prototype progress as current implementation. Those claims now
  belong to [historical recovery context](docs/archive/2026-06/MIGRATION.md), not current status.
- `actions`, `.github-private`, and `demo-repository` were deleted on GitHub and locally on October 7.
- The two active repositories are `wsr` and `.github`; the profile generator remains legacy maintenance.

## Documentation ownership and synchronization

WSR owns accepted decisions (`PLAN.md`), architecture, implementation accounting, security contracts,
and delivery gates. Organization docs summarize and link to them. Keep profile and template identical.
Use the same status labels and distinguish prototype evidence from checked-out code.

The implementation sequence is local execution → reuse inside GitHub Actions → possible independent CI.
Fixed Wasmtime/Wasmer/WASI selections, universal compatibility, automatic JS-to-Wasm conversion,
zero-container requirements, and performance guarantees are not accepted current commitments.

## Follow-up gates

1. Review coordinated documentation diffs in both repositories, including untracked documents and
   archived drafts. Publishing one repository alone may temporarily leave public links/content stale.
2. Review profile automation before any reactivation; changing a template is not fixing its generator.
3. If recovery is authorized, inspect prototype code in isolation, retain the original stash, run
   relevant tests, and compare recovered behavior against current decisions before selecting code.
4. Continue the open architecture decisions, then follow the
   [WSR delivery roadmap](https://github.com/ectorial/wsr/blob/main/ROADMAP.md).

The [older DESIGN/MIGRATION/TASKS drafts](docs/archive/2026-06/README.md) retain historical details.
Their commands, repository inventory, version claims, and completion statements are not current instructions.
