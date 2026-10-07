# ectorial

Pre-alpha tooling for running and debugging CI locally, then reusing the engine inside GitHub Actions.

## Current status

[WSR](https://github.com/ectorial/wsr) is currently a Rust workspace and CLI scaffold.
Argument parsing and early shared types exist; workflow inspection, execution, and sandbox enforcement
are not implemented in the checked-out code. Local unpublished prototype work is preserved separately
and is not a supported release.

## Accepted direction — planned

- A documented GitHub Actions compatibility subset with explicit diagnostics.
- The Component Model as a core deny-by-default security boundary.
- An isolated system backend for existing tools; reject execution when restrictions cannot be enforced.
- Linux jobs from macOS and Linux machines first; native macOS/Windows jobs later.
- Containment of malicious workloads on a single-user machine.
- Explicit owner-authorized broad runner access for compatibility, with scope/syntax still open.
- Local CI first, reuse inside GitHub Actions next, and possible independent CI later.

Concrete runtimes, outer isolation, CPU architectures, initial compatibility coverage, and the
Actions wrapper contract remain open. No supported execution quick start, native action catalog,
component registry, complete compatibility guarantee, or measured performance claim is available.

## Repositories and documentation

| Repository | Responsibility |
| --- | --- |
| [wsr](https://github.com/ectorial/wsr) | Product design, CLI, and future workflow engine |
| [.github](https://github.com/ectorial/.github) | Organization profile, governance, and summaries |

WSR's [decision record](https://github.com/ectorial/wsr/blob/main/PLAN.md),
[implementation checklist](https://github.com/ectorial/wsr/blob/main/CHECKLIST.md), and
[roadmap](https://github.com/ectorial/wsr/blob/main/ROADMAP.md) own the detailed story.
Organization summaries follow those records. Design decisions describe planned behavior;
the implementation checklist records what is present in the current code.
