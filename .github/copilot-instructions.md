# Repository instructions

## Ownership

This is `ectorial/.github`: organization profile, governance, and documentation summaries.
The core product and technical specification live in `ectorial/wsr`. The Node code in `src/`
is legacy profile maintenance, not the future CI engine or GitHub App.

## Documentation

Use WSR `PLAN.md` for accepted decisions and open proposals, `CHECKLIST.md` for implementation
status, and `ROADMAP.md` for delivery gates. Current WSR is a scaffold; prototype implementation
is preserved locally and must not be described as available functionality.

Keep `profile/README.md` and `profile/README.md.tpl` byte-identical. Separate current scaffold,
preserved prototype, accepted design (planned), and open proposals. Do not introduce independent
runtime/version commitments, complete compatibility claims, or unmeasured performance guarantees.

The retained repositories are `.github` and `wsr`. `actions`, `.github-private`, and `demo-repository`
were deleted on October 7, 2026. Files under `docs/archive/` are historical references, not current instructions.

## Legacy automation

Keep source changes focused and preserve existing behavior unless the task requests a change.
Never expose authentication tokens. Profile template generation requires separate review before
reactivation; documentation reconciliation does not authorize external writes or workflow enablement.
