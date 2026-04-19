<div align="center">

# ectorial

### ⚡ The Wasm-native CI/CD ecosystem.

**Local-first. Millisecond cold starts. Zero Docker.**
Built on Rust, powered by WebAssembly (WASI Preview 3) and the Wasm Component Model.

[![Status](https://img.shields.io/badge/status-public%20alpha-8A2BE2?style=flat-square)](#)
[![Wasm](https://img.shields.io/badge/WASI-Preview%203-654FF0?style=flat-square&logo=webassembly&logoColor=white)](https://webassembly.org/)
[![Rust](https://img.shields.io/badge/Built%20with-Rust-B7410E?style=flat-square&logo=rust&logoColor=white)](https://rust-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-000?style=flat-square)](./LICENSE)

</div>

---

## 🚀 Meet `wsr` — the Workflow Sandboxed Runner

`wsr` is a ridiculously fast, Rust-based CI/CD orchestrator that runs your pipelines as **Wasm components** — not containers, not VMs. Think of it as what [`uv`](https://github.com/astral-sh/uv) did for Python packaging, applied to the entire CI/CD stack.

> **Docker virtualizes the computer. WSR virtualizes the task.**

```bash
# Install the runner
curl -fsSL https://ectorial.dev/install.sh | sh

# Run a native ectorial workflow locally (sub-second)
wsr run wsr.toml

# Or run your existing GitHub Actions — locally, in milliseconds
wsr actions run
```

`wsr` automatically selects the right execution engine for each job — you never configure it manually.

---

## 😩 The Problem

Modern CI/CD is stuck in the 2015 container era:

| Standard GitHub Actions | What it actually costs you |
| --- | --- |
| 🐳 Every job spins up a Docker image | **15–60s** of pure cold-start overhead |
| 🚢 Runs only on GitHub's cloud runners | No real way to test locally |
| 📝 Typo in your YAML? | Push, wait 5 minutes, watch it fail, repeat |
| 🧱 Actions are JS/Docker/composite blobs | Tied to Node 20, a specific base image, or bash-in-YAML |
| 🐢 Caching, setup, restore… | Measured in seconds, not milliseconds |

## ✨ The ectorial Solution

The core insight: **OS-level virtualization is the wrong abstraction for CI tasks.** Docker virtualizes the entire machine so one process can run. WSR moves down a level — to **instruction-level virtualization** via WebAssembly — so the task itself becomes the isolation unit. No daemon. No image pull. No boot sequence.

```
┌─────────────────────────────────────────────────────────────────┐
│  wsr  →  Engine Selector  →  Wasm Isolate  →  Signed Component  │
│          (auto-detected)      ≈ 1–3 ms cold start (Tier 1)      │
└─────────────────────────────────────────────────────────────────┘
```

- ⚡ **Sub-millisecond to low-millisecond cold starts** — no container runtime, no daemon.
- 🏠 **True local-first.** `wsr actions run` executes your real workflow on your laptop with full fidelity.
- 🔐 **Sandboxed by default.** WASI capability-based security — components only touch what you explicitly grant.
- 🧩 **Polyglot.** Write components in Rust, Go, Python, C/C++, or JS. They all compile to the same Wasm ABI.
- 🌊 **Natively async** on WASIp3 — real concurrency, no blocking-thread-per-step nonsense.
- 🐳 **Zero Docker.** Not "less Docker" — even heavy toolchains like `rustc` run sandboxed inside Wasm, not containers.

---

## 🧠 Core Architecture — The Tiered Execution Engine

`wsr` automatically selects the best execution engine for each job based on what the job requires. Both runtimes expose a unified interface back to the orchestrator — **jobs communicate across tiers transparently**, with no special wiring needed.

The promotion rule is simple: if any step in a job requires capabilities beyond strict WASI, the **entire job** is promoted to the appropriate tier. You never configure this manually.

---

### Tier 1 — The Vault 🔒 &nbsp;(Wasmtime + WASI Preview 3)

**The default. Every job that can run here, does.**

This tier uses [Wasmtime](https://wasmtime.dev/) — the reference WASI runtime from the Bytecode Alliance — and runs natively-built [`ectorial/actions`](https://github.com/ectorial) as signed Wasm Components with typed [WIT](https://component-model.bytecodealliance.org/design/wit.html) interfaces.

| Property | Value |
| --- | --- |
| Cold start | **~1–3 ms** |
| Security model | WASI capability-based (strict) |
| Component format | Wasm Component Model |
| Target actions | `ectorial/*` native catalog |

**Philosophy: Strict security and speed.** Strict WASI means strict sandboxing — no ambient authority, no implicit syscalls, no surprises. The capability model is enforced at the ABI boundary. Components can only touch what you explicitly grant.

This is the long-term standardization target for the entire ecosystem. Every action in the `ectorial/actions` catalog runs here, and the catalog grows to eventually make every other tier unnecessary.

---

### Tier 2 — The Workshop 🔧 &nbsp;(Wasmer + WASIX)

**The compatibility hotfix layer. Used when Tier 1 isn't enough yet.**

When `wsr` detects that a job requires features that strict WASI doesn't yet support — process spawning (`fork`/`exec`), POSIX threads, full networking — it automatically promotes the job to [Wasmer](https://wasmer.io/) with the [WASIX](https://wasix.org/) extension set. WASIX virtualizes a POSIX-compatible OS surface *inside* the Wasm sandbox, without breaking out to a real container or VM.

| Property | Value |
| --- | --- |
| Cold start | **Low ms to tens of ms** (toolchain-dependent) |
| Security model | WASIX sandbox (POSIX-compatible, no host OS escape) |
| Component format | Plain Wasm modules |
| Target actions | Heavy toolchains (`rustc`, LLVM), complex binaries, GHA Marketplace actions without a Tier 1 equivalent |

**Philosophy: Pragmatic portability.** This tier exists because the WASI ecosystem is still maturing — not because containers are acceptable. WASIX lets us run `rustc` via LLVM, existing GitHub Marketplace actions, and other complex binaries without requiring users to rewrite their entire pipeline from scratch. It eliminates Docker even where Tier 1 can't reach yet.

> **WASIX is explicitly transitional.** As `ectorial/actions` grows and WASI Preview 3 matures, Tier 2 coverage shrinks. The goal is to make Tier 1 sufficient for everything. We maintain Tier 2 as long as it keeps you off Docker — not a day longer.

---

### Tier 3 — The Bridge 🌉 &nbsp;(GHA-Compatible Polyfill)

**Drop-in compatibility for your existing `.github/workflows/*.yml` files.**

This isn't a separate runtime — it's the resolver layer. When `wsr` runs a standard GitHub Actions workflow, it maps each `uses:` reference through the Component Resolver. Steps with a native `ectorial/*` equivalent run on Tier 1. Steps that need WASIX features run on Tier 2. Your YAML is untouched; the tier selection is silent.

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
│  (no equivalent yet)    ──▶  ⚠  advisory warning     │
└──────────────────────────────────────────────────────┘
```

No migration. No rewrite. Your existing pipeline — faster, locally, without Docker.

---

## 🪄 How the Polyfill Magic Works

When `wsr` sees a standard action reference, it resolves it against the `ectorial/*` component registry:

```yaml
# Your existing .github/workflows/ci.yml — untouched
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
  with:
    node-version: 22
- uses: actions/cache@v4
```

```
          ┌─────────────────────────────────────┐
          │   wsr actions run                   │
          │   ──────────────────                │
          │   actions/checkout@v4    ─────┐     │
          │   actions/setup-node@v4  ─────┤     │
          │   actions/cache@v4       ─────┤     │
          └───────────────────────────────┼─────┘
                                          ▼
                              ┌───────────────────────┐
                              │  Component Resolver   │
                              └───────────┬───────────┘
                                          ▼
          ┌───────────────────────────────────────────────────┐
          │   ectorial/checkout    (Rust → Wasm)  2ms · Tier 1│
          │   ectorial/setup-node  (Rust → Wasm)  3ms · Tier 1│
          │   ectorial/cache       (Rust → Wasm)  1ms · Tier 1│
          └───────────────────────────────────────────────────┘
                 same inputs • same outputs • 100× faster
```

Same `with:` inputs. Same outputs. Same semantics. Different universe of performance.

---

## 📦 Explore the Ecosystem

| Repo | What it is |
| --- | --- |
| [**`wsr`**](https://github.com/ectorial/wsr) | The Rust CLI & orchestrator — start here |
| [**`checkout`**](https://github.com/ectorial/checkout) | Wasm-native drop-in for `actions/checkout` |
| [**`setup-node`**](https://github.com/ectorial/setup-node) | Wasm-native drop-in for `actions/setup-node` |
| [**`setup-python`**](https://github.com/ectorial/setup-python) | Wasm-native drop-in for `actions/setup-python` |
| [**`cache`**](https://github.com/ectorial/cache) | Content-addressed cache, built for Wasm isolates |
| [**`upload-artifact`**](https://github.com/ectorial/upload-artifact) | Artifact I/O via WASI streams |
| [**`wit`**](https://github.com/ectorial/wit) | Shared WIT interfaces for all ectorial components |
| [**`docs`**](https://github.com/ectorial/docs) | Guides, spec, and the component authoring handbook |

---

## 🧪 Try it in 60 seconds

```bash
# 1. Install
curl -fsSL https://ectorial.dev/install.sh | sh

# 2. Drop into any repo with .github/workflows/*.yml
cd your-project

# 3. Run your CI locally. For real.
wsr actions run ci.yml
```

The first run pulls pre-compiled Wasm components. Every run after that is **cold-start in milliseconds**, fully offline-capable.

---

## 🤝 Contributing

ectorial is built in the open. Whether you want to author a new component, improve the orchestrator, or harden the WASIp3 runtime — we'd love your help.

- 📖 Read the [Contributing Guide](../CONTRIBUTING.md)
- 💬 Join the conversation in [Discussions](https://github.com/orgs/ectorial/discussions)
- 🐛 File issues on the relevant repo
- ⭐ Star [`wsr`](https://github.com/ectorial/wsr) to follow the launch

---

<div align="center">

**Stop waiting on runners. Start shipping.**

*Built with 🦀 Rust, 🕸️ Wasm, and an obsession with cold-start latency.*

</div>
