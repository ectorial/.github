# ectorial organization documentation

This repository owns the organization profile, governance, and a short cross-repository overview.
[WSR](https://github.com/ectorial/wsr) owns the product design and implementation records.

## Current repositories

| Repository | Responsibility | Current status |
| --- | --- | --- |
| [`wsr`](https://github.com/ectorial/wsr) | Local CI engine and technical design | Pre-alpha CLI/workspace scaffold; execution is not implemented |
| [`.github`](https://github.com/ectorial/.github) | Organization profile, governance, and documentation summaries | Shared product/status documentation; legacy profile generator retained |

`actions`, `.github-private`, and `demo-repository` were deleted from GitHub and local storage
on October 7, 2026. A future catalog or service is not an existing repository dependency.

## Documentation ownership

- [WSR PLAN.md](https://github.com/ectorial/wsr/blob/main/PLAN.md): accepted decisions and open proposals.
- [WSR ARCHITECTURE.md](https://github.com/ectorial/wsr/blob/main/ARCHITECTURE.md): current scaffold and target boundaries.
- [WSR CHECKLIST.md](https://github.com/ectorial/wsr/blob/main/CHECKLIST.md): implementation status.
- [WSR ROADMAP.md](https://github.com/ectorial/wsr/blob/main/ROADMAP.md): delivery gates.
- [DESIGN.md](DESIGN.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [ROADMAP.md](ROADMAP.md): organization summaries.
- [MIGRATION.md](MIGRATION.md) and [TASKS.md](TASKS.md): reconciliation and publication coordination.

Use **Current scaffold**, **Preserved prototype**, **Accepted design** (planned), and **Open proposal**
consistently. Design approval is not implementation completion. Publish coordinated documentation
changes together and verify cross-repository links against the resulting revisions.

Keep [profile/README.md](profile/README.md) and [profile/README.md.tpl](profile/README.md.tpl)
byte-identical. The existing Node generator is profile maintenance, not a CI controller; no automation
lifecycle change is implied by documentation edits. See [CONTRIBUTING.md](CONTRIBUTING.md).
