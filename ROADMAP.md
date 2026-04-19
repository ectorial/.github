# Ectorial — Roadmap

This is the **organization-level roadmap**, sequenced around `ectorial/wsr` because WSR is the prerequisite for everything else in the ecosystem. No action catalog, no GHA polyfill, no cloud runner — without a working engine first.

Each milestone is a **capability gate**: it unlocks the next layer. The ecosystem grows in layers, not in parallel, because adding actions before the runtime can reliably execute them wastes everyone's time.

---

## Guiding Principle

> Ship less Docker with every release.

Every milestone should measurably reduce the number of real-world CI workflows that require a container runtime. Progress is tracked by the ratio of the top-100 most-used GitHub Actions Marketplace steps coverable by Tier 1 (`ectorial/actions`) or Tier 2 (WASIX) without touching Docker.

The long-term goal is to make Tier 1 sufficient for everything. Tier 2 exists to bridge the gap while `ectorial/actions` matures — not as a permanent destination.

---

## Milestone Overview

```
  v0.1 ──▶ v0.2 ──▶ v0.3 ──▶ v0.4 ──▶ v0.5 ──▶ v1.0
  Exec     GHA      Tier 2   Registry  Actions  Production
  Core     Polyfill  WASIX   + Signing Coverage   Ready
```

---

## v0.1 — Execution Core

**Status:** Public Alpha

**Goal:** Prove the runtime works end-to-end. A developer can write a `wsr.toml`, run it locally against real `ectorial/actions`, and get a result — without Docker, without a cloud runner.

### WSR
- [x] `wsr run wsr.toml` — sequential job execution
- [x] Wasmtime integration (Tier 1, WASI Preview 2/3 components)
- [x] Capability grant system (filesystem, environment)
- [x] `wsr.toml` workflow format (steps, `uses`, `run`, `with`)
- [ ] Parallel step execution within a job
- [ ] Component signature verification at execution time

### Actions (first catalog)
- [ ] `ectorial/checkout` — Tier 1
- [ ] `ectorial/setup-node` — Tier 1

### Ecosystem
- [ ] `ectorial/wit` — initial WIT interface definitions for `checkout` and `setup-*` patterns
- [ ] Internal component registry (read-only, used by `wsr`)

---

## v0.2 — GHA Polyfill Layer

**Goal:** Make `wsr actions run` work for the most common Node/Python CI workflows without any migration. A developer drops `wsr` into an existing repo and their `.github/workflows/*.yml` runs locally, faster, without Docker.

### WSR
- [ ] `wsr actions run <file>` — parse and execute `.github/workflows/*.yml`
- [ ] Component Resolver: `actions/*` → `ectorial/*` reference mapping
- [ ] Advisory warnings for unresolved steps (no silent Docker fallback)
- [ ] Job dependency graph (`needs:`) support
- [ ] `env:` and `secrets:` handling (capability-scoped)
- [ ] `wsr diagnose <file>` — report which steps can and can't be resolved, and why

### Actions
- [ ] `ectorial/setup-python` — Tier 1
- [ ] `ectorial/cache` — Tier 1 (content-addressed, offline-capable)
- [ ] `ectorial/upload-artifact` / `ectorial/download-artifact` — Tier 1

### Ecosystem
- [ ] `ectorial/wit` — artifact, cache, and secrets interface definitions
- [ ] Public component registry (read)
- [ ] `wsr publish` — community action authors can publish signed components

---

## v0.3 — Tier 2: WASIX Integration

**Goal:** Eliminate Docker for heavy toolchains. `rustc` (via LLVM), complex build systems, and GHA Marketplace actions that expect a POSIX environment run sandboxed inside Wasm — not in a container.

### WSR
- [ ] Wasmer + WASIX integration (Tier 2 engine)
- [ ] Automatic tier detection: if any step in a job requires WASIX capabilities, promote the entire job
- [ ] Unified job output interface across Tier 1 and Tier 2 (outputs pass as typed values, not raw file I/O)
- [ ] Tier 2 capability scoping (WASIX syscalls are virtualized, not forwarded to host)

### Actions
- [ ] `ectorial/setup-rust` — Tier 2 initially (`rustc` via LLVM + WASIX)
- [ ] `ectorial/setup-go` — Tier 1 (Go has strong WASI support)

### Ecosystem
- [ ] WASIX compatibility matrix: which GHA Marketplace actions run under Tier 2, and what their limitations are
- [ ] `ectorial/wit` — inter-tier output passing interfaces
- [ ] `ectorial/docs` — Tier 2 authoring guide, WASIX ceiling documentation

---

## v0.4 — Registry, Signing, and Cache

**Goal:** Production-grade supply chain. The component registry is trustworthy, the cache layer is fast enough for teams, and external authors can publish components that `wsr` will run.

### WSR
- [ ] Component signature verification at resolution time (Tier 1 required; Tier 2 best-effort)
- [ ] Content-addressed component cache (digest-keyed, offline-capable, shared across jobs)
- [ ] Registry authentication (`wsr login`)
- [ ] `wsr build` — first-class component build pipeline (wraps `cargo component`, `tinygo`, etc.)

### Ecosystem
- [ ] Public component registry (read + authenticated write)
- [ ] Signing key infrastructure for the `ectorial/actions` catalog
- [ ] `ectorial/docs` — complete component authoring handbook (WIT interfaces, build, publish, sign)

---

## v0.5 — Actions Coverage Milestone

**Goal:** Cover 80% of the most-used GitHub Actions Marketplace steps under Tier 1 or Tier 2. Begin migrating Tier 2 actions to Tier 1 — demonstrating that the WASIX layer is shrinking as intended.

### Coverage targets

| Action | Target tier | Introduced |
| --- | --- | --- |
| `actions/checkout` | Tier 1 | v0.1 |
| `actions/setup-node` | Tier 1 | v0.1 |
| `actions/setup-python` | Tier 1 | v0.2 |
| `actions/cache` | Tier 1 | v0.2 |
| `actions/upload-artifact` | Tier 1 | v0.2 |
| `actions/setup-go` | Tier 1 | v0.3 |
| `actions/setup-rust` | Tier 2 → Tier 1 migration | v0.5 |
| `actions/setup-java` | Tier 2 → Tier 1 migration | v0.5 |
| `docker/build-push-action` | Tier 2 (WASIX) | v0.5 |
| `github/codeql-action` | Tier 2 (WASIX) | v0.5 |

### WSR
- [ ] Matrix job support (`strategy.matrix`)
- [ ] Conditional steps (`if:`) evaluation
- [ ] `wsr actions run` feature parity for the top-20 most-used GHA steps

---

## v1.0 — Production Ready

**Goal:** Stable public API, cloud runner mode, Tier 2 actively shrinking, community action ecosystem live. A team can replace GitHub's hosted runners with `wsr` in production with confidence.

### WSR
- [ ] Stable `wsr.toml` schema (semver-committed, no breaking changes without a major)
- [ ] **Infra-agnostic runner mode** — because WSR components are just Wasm, they can execute on any Wasm-capable compute. Target platforms:
  - **Cloudflare Workers / workerd** — Wasm runs natively; WSR jobs become Workers invocations with zero container overhead and global edge distribution
  - **Custom GitHub Actions runner** — implement the GitHub Actions runner protocol so `wsr` registers as a self-hosted runner, making any Wasm-capable machine a drop-in replacement for GitHub's hosted runners without changing a single workflow file
  - **Any OCI/Wasm-capable host** — the runner interface is a thin adapter; porting to new infra means writing a new adapter, not rewriting the engine
- [ ] Distributed job graph execution (parallel jobs across machines, infra-agnostic)
- [ ] `wsr.toml` → `.github/workflows/` export — for teams that still need to run on GitHub's cloud

### Ecosystem
- [ ] Community-authored component catalog (actions not in `ectorial/*`, authored and signed by third parties)
- [ ] Tier 1 coverage sufficient that Tier 2 is optional for the majority of real-world workflows
- [ ] WASI Preview 3 fully standardized upstream — official Tier 2 → Tier 1 migration guide published
- [ ] `ectorial/docs` — operator guide for self-hosted `wsr` cloud deployments

---

## Out of Scope (for now)

| Area | Why deferred |
| --- | --- |
| Windows / macOS host support | Linux host first; cross-platform is post-v1.0 |
| GUI / web dashboard | CLI-first, always |
| Managed runner hardware | Cloud runner is software; infrastructure is separate |
| Non-CI Wasm orchestration | WSR is a CI/CD tool; general-purpose Wasm scheduling is out of scope |
| Full Docker image compatibility | WASIX cannot run arbitrary ELF binaries without recompilation — see `ARCHITECTURE.md` |

---

## How to Read This Roadmap

Milestones are **capability gates**, not time-boxed sprints. A milestone is done when its stated goal is achievable end-to-end for a real workflow — not when a checklist is fully ticked.

Items marked **Tier 2 → Tier 1 migration** are actions where WASIX was the necessary bridge. Migrating them to Tier 1 is the explicit intended lifecycle: WASIX buys time, Tier 1 is the destination. The health of this roadmap is measured partly by how fast that migration column grows.
