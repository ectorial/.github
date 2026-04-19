# Ectorial — Organization Architecture

This document describes the **ecosystem-level architecture** of the ectorial organization: how repositories relate, where the boundaries lie, and what contracts cross those boundaries.

Internal implementation details — runtime internals, component authoring patterns, subsystem design — live in each repo's own `ARCHITECTURE.md`. This document is the map, not the terrain.

---

## The Core Principle

> **Docker virtualizes the computer. WSR virtualizes the task.**

Standard CI/CD treats every job as a machine to boot. Ectorial treats every job as a typed function to invoke. The isolation unit is the Wasm component, not the container. The security boundary is the WASI capability, not the network namespace.

This shift — from OS-level to instruction-level virtualization — is what makes millisecond cold starts possible and Docker unnecessary.

---

## Ecosystem Map

```
                     ┌──────────────────────────────────┐
                     │            developer              │
                     │  wsr.toml  /  .github/workflows  │
                     └─────────────────┬────────────────┘
                                       │
                                       ▼
                     ┌──────────────────────────────────┐
                     │           ectorial/wsr            │
                     │                                  │
                     │  • parses workflow definitions    │
                     │  • resolves action references     │
                     │  • selects execution tier         │
                     │  • orchestrates the job graph     │
                     │  • manages capability grants      │
                     └────────┬──────────────┬──────────┘
                              │              │
              ┌───────────────┘              └──────────────────┐
              ▼                                                  ▼
 ┌────────────────────────┐                    ┌────────────────────────────┐
 │  Tier 1: Wasmtime      │                    │  Tier 2: Wasmer + WASIX    │
 │  (WASI Preview 3)      │                    │  (POSIX compatibility)     │
 └───────────┬────────────┘                    └────────────────────────────┘
             │
             ▼
 ┌────────────────────────┐
 │   ectorial/actions     │
 │   (Wasm Components)    │──────────────────▶  ectorial/wit
 │   signed + typed       │                     (shared WIT interfaces —
 └────────────────────────┘                      the ABI contract)
```

---

## Repository Roles

### `ectorial/wsr`

The core engine and CLI. Every other part of the ecosystem is a dependency on or a consumer of `wsr`.

**Owns:**
- Workflow parsing (`wsr.toml` and `.github/workflows/*.yml`)
- The Component Resolver — maps action references to Wasm components
- Tier selection and job graph orchestration
- Capability grant management
- Component registry client (fetch, verify, cache)

**Does not own:** Wasmtime/Wasmer internals (upstream dependencies), WIT interface definitions, action implementations.

See [`ectorial/wsr/ARCHITECTURE.md`](https://github.com/ectorial/wsr) for internal design.

---

### `ectorial/wit`

The shared ABI contract for the entire ecosystem. Every `ectorial/actions` component is typed against interfaces defined here. This repo is the single source of truth for:

- Host interfaces provided by `wsr` (filesystem, networking, environment, secrets)
- Cross-component interfaces (artifact passing, cache, inter-job outputs)
- Action input/output schemas

**Changing a WIT interface is a breaking change** for any component that implements it. Changes follow semantic versioning with explicit deprecation cycles before removal.

---

### `ectorial/actions/*`

Individual Wasm components implementing CI primitives (`checkout`, `setup-node`, `setup-python`, `cache`, `upload-artifact`, …). Each action:

- Implements one or more WIT interfaces from `ectorial/wit`
- Compiles to a signed Wasm Component (`.wasm` + signature)
- Targets **Tier 1 exclusively** (Wasmtime + WASI Preview 3)
- Is published to the component registry and resolved by `wsr`

Each action repo has its own `ARCHITECTURE.md` covering implementation specifics.

---

### `ectorial/docs`

Authoritative guide for component authors, operators, and contributors. Covers the component authoring lifecycle, WIT interface contracts, the capability model, registry publishing, and the WASIX migration path.

---

## The Tiered Execution Model

`wsr` dispatches each job to one of three tiers. Tier selection is automatic — users never configure it. Both runtime engines expose a unified interface back to the orchestrator; **jobs communicate across tiers transparently**.

**Promotion rule:** if any step in a job requires capabilities beyond strict WASI, the entire job is promoted to the appropriate tier.

---

### Tier 1 — The Vault (Wasmtime + WASI Preview 3)

The default. Every job that can run here, does.

| Property | Value |
| --- | --- |
| Runtime | [Wasmtime](https://wasmtime.dev/) (Bytecode Alliance) |
| Cold start | ~1–3 ms |
| Security model | WASI capability-based (strict) |
| Module format | Wasm Component Model |
| Actions | `ectorial/*` native catalog |

**Cross-repo contracts this tier imposes:**
- Components must implement WIT interfaces from `ectorial/wit`
- Components must be signed; the registry enforces this at publish time, `wsr` verifies at resolution time
- Capabilities are granted by `wsr` at job start — components have no ambient authority

---

### Tier 2 — The Workshop (Wasmer + WASIX)

The compatibility hotfix layer. Activated when Tier 1 isn't sufficient yet.

| Property | Value |
| --- | --- |
| Runtime | [Wasmer](https://wasmer.io/) + [WASIX](https://wasix.org/) |
| Cold start | Low ms to tens of ms (toolchain-dependent) |
| Security model | WASIX sandbox (POSIX-compatible, no host OS escape) |
| Module format | Plain Wasm modules (not Component Model) |
| Actions | Heavy toolchains (`rustc`, LLVM), complex binaries, GHA Marketplace actions |

WASIX virtualizes POSIX syscalls — `fork`/`exec`, threads, sockets — inside the Wasm sandbox without breaking out to the host kernel. This eliminates Docker even for workloads that Tier 1 can't yet handle.

**Important ceiling:** Tier 2 requires binaries to be compiled to `wasm32-wasix`. It cannot execute arbitrary pre-built Linux ELF binaries or pull opaque Docker images. Obscure syscalls (`ptrace`, raw sockets, mount, kernel namespaces) are out of scope.

**WASIX is explicitly transitional.** As `ectorial/actions` coverage grows and WASI Preview 3 matures, Tier 2 workloads migrate to Tier 1. We maintain Tier 2 as long as it keeps workflows off Docker — not a day longer.

---

### Tier 3 — The Bridge (GHA-Compatible Polyfill)

Drop-in compatibility for existing `.github/workflows/*.yml` files. Not a separate runtime — the resolver layer.

When `wsr` runs a standard GitHub Actions workflow, the Component Resolver maps each `uses:` reference to a Wasm component, then assigns it to Tier 1 or Tier 2. The user's YAML is untouched.

```
wsr actions run ci.yml
         │
         ▼
┌──────────────────────────────────────────────────────┐
│                  Component Resolver                  │
│                                                      │
│  actions/checkout@v4    ──▶  ectorial/checkout       │  Tier 1 · ~2ms
│  actions/setup-node@v4  ──▶  ectorial/setup-node     │  Tier 1 · ~3ms
│  actions/setup-rust@v1  ──▶  ectorial/setup-rust     │  Tier 2 · WASIX
│  (no equivalent)        ──▶  ⚠  advisory warning     │
└──────────────────────────────────────────────────────┘
```

The resolver never silently falls back to Docker. If no Wasm path exists, the step is flagged, not silently containerized.

---

## The Component Resolver

The resolver is the primary integration contract between `wsr` and the rest of the ecosystem. It lives inside `wsr` but its behavior is defined here because it determines how new `ectorial/actions` repos enter the resolution chain.

**Resolution order for `uses: owner/action@ref`:**

1. Check local component cache (content-addressed, digest-keyed)
2. Check `ectorial/*` registry for a native Tier 1 equivalent → assign Tier 1
3. Check for a WASIX-compatible build → assign Tier 2
4. No match → emit advisory warning; leave step unresolved

The resolver never introduces a runtime that bypasses the sandbox.

---

## Security Model

The security boundary is the Wasm sandbox, not the OS process boundary.

- **No ambient authority.** Components cannot access the filesystem, network, or environment unless `wsr` explicitly grants it via the WASI capability model.
- **Capabilities are declared or inferred.** `wsr.toml` can declare grants explicitly; `wsr` also infers minimum required capabilities from a component's WIT interface imports.
- **Signed components.** `wsr` verifies component signatures before execution. Unsigned components are rejected in Tier 1. Tier 2 applies best-effort verification.
- **WASIX preserves sandboxing.** POSIX syscalls are virtualized inside the sandbox — they are not forwarded to the host kernel.

---

## Component Lifecycle

```
  Author              Registry             wsr              Runtime
    │                    │                  │                  │
    │  wsr build         │                  │                  │
    │  wsr publish ─────▶│ sign + store     │                  │
    │                    │                  │                  │
    │                    │    resolve ref ◀─┤                  │
    │                    │ return digest ──▶│                  │
    │                    │                  │ verify sig       │
    │                    │                  │ execute ────────▶│
    │                    │                  │◀──────── outputs │
```

---

## What This Org Does Not Own

- **Wasmtime** — upstream at [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)
- **Wasmer** — upstream at [wasmerio/wasmer](https://github.com/wasmerio/wasmer)
- **The WASI standard** — governed by the W3C WebAssembly CG
- **GitHub Actions runner protocol** — `wsr` implements GHA compatibility; it does not define or extend the protocol
