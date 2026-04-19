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

```bash
# Install the runner
curl -fsSL https://ectorial.dev/install.sh | sh

# Run a native ectorial workflow locally (sub-second)
wsr run wsr.toml

# Or run your existing GitHub Actions — locally, in milliseconds
wsr actions run
```

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

```
┌──────────────────────────────────────────────────────────┐
│  wsr  →  Wasmtime Isolate  →  Signed Wasm Component      │
│         ≈ 1–3 ms cold start       pre-compiled, cached   │
└──────────────────────────────────────────────────────────┘
```

- ⚡ **1–3 ms cold starts** via Wasmtime isolates — no container runtime, no daemon.
- 🏠 **True local-first.** `wsr actions run` executes your real workflow on your laptop with full fidelity.
- 🔐 **Sandboxed by default.** WASI capability-based security — components can only touch what you grant.
- 🧩 **Polyglot.** Write components in Rust, Go, Python, C/C++, or JS. They all compile to the same Wasm ABI.
- 🌊 **Natively async** on WASIp3 — real concurrency, no blocking-thread-per-step nonsense.

---

## 🧠 Core Philosophy — The Dual Engine

`wsr` ships with **two engines** under one CLI:

### 1. 🦀 The Native Engine — `wsr run wsr.toml`

A first-class, local-first workflow format designed around Wasm components from day one. Declarative, async, typed via [WIT](https://component-model.bytecodealliance.org/design/wit.html) interfaces.

```toml
# wsr.toml
[workflow.ci]
on = ["push", "pull_request"]

[[workflow.ci.steps]]
uses = "ectorial/checkout"

[[workflow.ci.steps]]
uses = "ectorial/setup-node"
with = { version = "22" }

[[workflow.ci.steps]]
run = "npm test"
```

### 2. 🐙 The Drop-In Replacement — `wsr actions run`

Point it at any existing `.github/workflows/*.yml` file and it Just Works™. `wsr` parses the standard GitHub Actions schema and **transparently aliases** each `uses:` step to an equivalent pre-compiled Wasm component from this org.

No migration. No rewrite. Your existing pipeline — **100× faster, locally**.

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
          ┌───────────────────────────────────────────┐
          │   ectorial/checkout      (Rust → Wasm)    │  2ms
          │   ectorial/setup-node    (Rust → Wasm)    │  3ms
          │   ectorial/cache         (Rust → Wasm)    │  1ms
          └───────────────────────────────────────────┘
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
