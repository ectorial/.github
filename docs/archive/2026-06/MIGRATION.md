> Historical unpublished draft, preserved during the October 7, 2026 documentation reconciliation.
> This is not current status, policy, or an executable migration plan. References and commands
> describe the original June-era context and may refer to deleted repositories or old paths.
> Use the active [organization overview](../../../README.md) and
> [WSR decision record](https://github.com/ectorial/wsr/blob/main/PLAN.md) instead.

# ectorial migration plan

## Status

This document describes a staged migration from the current ectorial
organization to the architecture proposed in [`DESIGN.md`](DESIGN.md). It is a
plan, not a statement of implemented behavior.

The migration deliberately starts with inspection and planning rather than
execution. Each phase has an exit gate; later phases should not begin merely
because their repository structure has been created.

## Migration objective

Move from the current pre-alpha workflow parser and repository placeholders to
a CI/CD system with:

- GitHub-native triggering and monitoring without GitHub Actions execution;
- a provider-neutral pipeline intermediate representation;
- a GitHub Actions YAML compatibility frontend;
- a WebAssembly Component Model execution tier;
- an isolated system execution tier for arbitrary POSIX, container, platform,
  and hardware workloads;
- immutable source snapshots, artifacts, and structured validation evidence;
- explicit policy, capability, and trust boundaries;
- consistent local and remote validation where the workload permits it.

The migration is complete when the end-to-end acceptance criteria near the end
of this document pass. Creating the proposed crates or repositories is not, by
itself, progress toward completion.

## Progress

As of 2026-06-27:

- Phase 0 is in progress: repository roles and public status are documented,
  `wsr` follows the Rust template's development structure, and disposition of
  legacy organization automation still requires approval.
- Phase 1 is implemented locally in `wsr`: `wsr inspect` emits deterministic
  text or JSON reports, classifies the initial GHA subset, and preserves unknown
  workflow, job, strategy, and step fields as diagnostics.
- Phase 2 is implemented locally in `wsr`: the provider-neutral IR models source
  identity, dependencies, matrices, validation planes, execution tiers,
  requirements, and capabilities; the GHA adapter translates the current
  rust-template fixture and validates the resulting plan.
- Phase 3 is implemented locally in `wsr`: source trees are normalized under
  Git ignore rules, blobs and manifests are addressed by SHA-256, snapshots can
  be materialized read-only, and evidence records exact identities and grants.
  Symlinks are recorded but intentionally cannot be materialized yet.
- `wsr plan` connects source capture, GHA translation, plan validation, and
  provider-neutral JSON without executing workflow steps.
- Phase 4 is not implemented pending the runtime/MSRV decision recorded in
  `TASKS.md`.
- Phase 5 has a partial development implementation: `wsr` can run a local system
  command with cleared environment, bounded scratch paths, timeout termination,
  capped output, and explicit capability rejection. Production isolation is not
  selected, and this backend is not approved for hostile workloads.
- Phase 7 has an adapter-core implementation only: GitHub webhook signatures are
  verified and supported events translate into provider-neutral requests with
  process-local or single-host durable deduplication. There is no HTTP service,
  shared transactional state, App credential flow, scheduler, Checks API write,
  or reconciliation yet. Internal invocation transitions and Checks payload
  projection are implemented and tested.

## Current state

### `ectorial/.github`

Current responsibilities:

- organization profile and governance files;
- organization-level architecture, roadmap, and status language;
- legacy `gh-auto` Node.js code that queries GitHub and generates profile
  content;
- GitHub workflow automation for this repository.

Current design artifacts:

- `ARCHITECTURE.md` describes the implemented organization structure;
- `ROADMAP.md` identifies inspection as the next product milestone;
- `DESIGN.md` records the target CI/CD architecture.

The legacy Node.js code is not the planned GitHub App adapter and must not become
one accidentally without an explicit decision.

### `ectorial/wsr`

Current responsibilities:

- Rust workspace and CLI scaffolding;
- `wsr init` and `wsr run` command parsing;
- `wsr.json` configuration helpers;
- initial typed parsing of selected GitHub Actions workflow fields;
- one Rust-template GitHub Actions fixture;
- placeholder engine, provider, sandbox, and sync modules.

It does not currently execute workflows, expand a job graph, evaluate GitHub
expressions, resolve actions, run WebAssembly, enforce capabilities, schedule
remote workers, or publish GitHub Checks.

### `ectorial/actions`

Current responsibilities:

- placeholder for a future native action catalog.

It does not currently contain a component format, WIT world, registry metadata,
trust policy, or executable action components.

### `ectorial/cargo-xdist`

Current responsibilities:

- separate distributed Cargo test execution experiment.

It is not part of the current `wsr` product boundary. The migration must not make
the CI/CD architecture depend on it. It may later serve as a real workload or
integration fixture if that can be done without coupling the products.

### `ectorial/.github-private`

Current responsibilities:

- public placeholder repository despite its name;
- no product implementation or private organization profile content.

Its intended lifecycle is undefined and requires an explicit retain, privatize,
archive, rename, or remove decision.

### `ectorial/demo-repository`

Current responsibilities:

- private GitHub demonstration repository;
- example HTML and GitHub Actions workflows unrelated to `wsr` implementation.

It may be retained as a compatibility fixture source, but must not become a
product dependency.

## Target repository responsibilities

Repository boundaries should follow validated ownership and deployment needs,
not the boxes in an architecture diagram.

### `ectorial/.github`

Retain:

- organization profile and governance;
- organization-level `DESIGN.md`, this migration plan, and public status;
- cross-repository contribution and security policy where appropriate.

Do not place the pipeline engine, scheduler, worker runtime, component registry,
or GitHub App service here. Decide separately whether the legacy profile
generator is retained, replaced, or removed.

### `ectorial/wsr`

Use as the initial product repository and modular monolith. During the early
migration it should own:

- local CLI behavior;
- GHA workflow parsing and compatibility diagnostics;
- provider-neutral pipeline IR;
- planning, matrix expansion, expression handling, and tier classification;
- source snapshot identity;
- component runtime host and capability interfaces;
- initial local system backend abstraction;
- evidence and result models;
- protocol types shared with an initial remote proof of concept.

New crates should be extracted inside the workspace only when there is a real
dependency boundary. New repositories should be created only at the extraction
gates described below.

### `ectorial/actions`

Use for reviewed native components only after `wsr` has established:

- a versioned WIT world;
- component packaging and metadata;
- signing and digest rules;
- a conformance test harness;
- capability declaration and review policy.

The first component should validate the platform contract. It should not attempt
to reproduce an entire marketplace.

### `ectorial/cargo-xdist`

Keep independent. It may later validate system-tier scheduling or distributed
test workloads through public interfaces, but it must not supply private engine
APIs to `wsr`.

### `ectorial/.github-private` and `ectorial/demo-repository`

Keep outside the product runtime. Record an explicit lifecycle decision for
each during Phase 0. If `demo-repository` contributes workflow fixtures, copy or
pin those fixtures under `wsr` tests so remote repository mutation cannot change
compatibility behavior.

### Potential future repositories

The following are candidates, not approved repositories:

- a GitHub App/control-plane service;
- a remote worker agent;
- a component registry or registry service;
- a shared specification or SDK repository.

Create one only when all of these are true:

1. The boundary has executable code and tests in `wsr` or a prototype.
2. It requires an independent deployment, release cadence, security boundary,
   or language/toolchain.
3. Its protocol is explicit and versioned.
4. Moving it reduces coupling instead of creating a distributed monolith.

## Migration principles

- Preserve the current working parser while replacing its output incrementally.
- Add compatibility fixtures before broadening compatibility claims.
- Keep provider syntax out of the core pipeline IR.
- Separate source/runtime classification from component/system backend choice.
- Default ambiguous execution to the system tier.
- Keep authoritative state internal; treat GitHub Checks as a projection.
- Introduce one backend and one vertical slice at a time.
- Do not publish native components before their host contract is stable enough
  to test compatibility.
- Do not split repositories ahead of demonstrated ownership or deployment needs.
- Keep **Implemented**, **Next**, and **Planned** language synchronized across
  organization and repository documentation.

## Phase 0: establish the baseline

### Purpose

Create a trustworthy starting point before changing architecture.

### Changes

In `ectorial/.github`:

- link `DESIGN.md` and `MIGRATION.md` from the relevant organization docs;
- document whether legacy `gh-auto` profile generation is active, obsolete, or
  intentionally retained;
- keep public claims limited to implemented behavior.

In `ectorial/wsr`:

- complete or stabilize the in-progress workspace reorganization;
- ensure current parser, configuration, and CLI behavior have tests;
- record the current fixture behavior before changing the parser model;
- confirm the domain language in `CONTEXT.md` matches `DESIGN.md`.

In `ectorial/actions`:

- retain placeholder status;
- make no component format commitments yet.

In `ectorial/cargo-xdist`:

- make no product-integration changes.

For `.github-private` and `demo-repository`:

- record whether each repository is retained, repurposed, archived, made
  private/public, renamed, or removed;
- do not change visibility or delete repositories without explicit approval.

### Exit gate

- The `wsr` workspace builds and tests from a clean checkout.
- Current supported parser behavior is covered by tests.
- Organization docs make no claims beyond repository implementation.
- The legacy `.github` automation has an explicit disposition.
- `.github-private` and `demo-repository` have explicit lifecycle decisions.

## Phase 1: compatibility inspection

### Purpose

Turn the current GHA parser into a compatibility frontend that can explain what
it understands without executing anything.

### Changes in `wsr`

- Introduce a normalized inspection model separate from deserialized GHA types.
- Add an inspection CLI command or make `run --dry-run` produce the normalized
  plan without changing execution state.
- Classify at least:
  - `run:` steps;
  - `uses:` steps;
  - job dependencies;
  - structured and expression-based matrices;
  - conditions and outputs;
  - unsupported workflow, job, and step fields.
- Record source locations for actionable diagnostics where feasible.
- Add golden or snapshot tests for compatibility reports.
- Use the Rust-template CI workflow as the first acceptance fixture.
- Add fixtures only to represent a named compatibility requirement or bug.

### Required output

Every parsed construct is reported as:

- native candidate;
- emulation candidate;
- system fallback;
- unsupported.

These labels are inspection results, not execution promises.

### Exit gate

- The first fixture produces a deterministic normalized report.
- Unknown or unsupported fields are not silently discarded.
- GHA parsing types do not leak directly into future execution interfaces.
- No workflow command is executed.

## Phase 2: define the pipeline IR and planner

### Purpose

Establish the provider-neutral core model before adding runtimes.

### Changes in `wsr`

- Define stable internal identifiers for pipelines, jobs, operations, inputs,
  outputs, and evidence.
- Model immutable source revision and snapshot digests.
- Model job dependencies and matrix expansion.
- Model source-plane versus runtime-plane classification.
- Model component-tier versus system-tier execution requirements separately.
- Model explicit capabilities for filesystem, network, secrets, cache,
  artifacts, clocks, randomness, and hardware.
- Preserve compatibility origin and diagnostics as metadata rather than core
  semantics.
- Add planner validation for missing inputs, cycles, incompatible outputs,
  unsupported capabilities, and unavailable execution requirements.
- Serialize the IR for debugging and fixtures, without promising that the first
  serialization is a permanent public API.

### Repository rule

Keep the IR and planner in the `wsr` workspace. Extract crates only if tests show
a useful dependency direction, such as provider frontend -> IR <- execution
backend.

### Exit gate

- GHA fixtures translate into deterministic provider-neutral plans.
- A synthetic non-GitHub pipeline can construct the same IR without GHA types.
- Every operation records its validation plane and required execution tier.
- Invalid plans fail before scheduling.
- Planner tests require no WebAssembly runtime, container daemon, or GitHub API.

## Phase 3: immutable source and evidence

### Purpose

Create the data identity required for safe local/remote parity and caching.

### Changes in `wsr`

- Define source snapshot creation and normalization rules.
- Ensure ignored files, generated files, symlinks, executable bits, and
  submodules have explicit behavior.
- Address snapshots by digest and make them read-only to validators.
- Define a structured evidence envelope containing source, tool/component,
  policy, capability, environment, conclusion, finding, and artifact identities.
- Implement a local content store suitable for development.
- Keep storage behind interfaces that do not assume a future remote vendor.

### Exit gate

- Identical normalized source produces the same snapshot digest.
- Mutating the working tree after capture cannot change an in-flight snapshot.
- A no-op validation can emit deterministic evidence tied to the snapshot.
- Cache keys include all inputs that can affect the result or explicitly record
  why an input is intentionally excluded.

## Phase 4: first component execution

### Purpose

Validate the WebAssembly Component Model as the native execution contract.

### Changes in `wsr`

- Select one runtime for the first implementation while keeping runtime-specific
  types behind a narrow adapter.
- Adopt WASI Preview 2 as the assumed initial stable component baseline unless a
  recorded experiment demonstrates that Preview 3 is required immediately.
- Define the smallest WIT world needed for one read-only source analyzer.
- Provide only source read, structured logging, finding emission, and bounded
  scratch capabilities initially.
- Implement execution interruption, CPU/fuel or epoch limits, memory limits,
  output limits, and capability auditing.
- Execute the same component against the same snapshot through local CLI and a
  test worker harness.
- Add negative tests for denied filesystem, network, secret, and resource use.

### Changes in `actions`

- Add the first conformance component only after the WIT world and test harness
  exist in `wsr`.
- Pin build tools and publish the component by immutable digest.
- Record required capabilities and supported WIT/WASI versions.
- Do not add multiple components until the first component's versioning and
  upgrade path have been exercised.

### Exit gate

- The component executes locally and in the worker harness with the same result.
- Undeclared capabilities are denied and tested.
- Evidence identifies the source, component, runtime environment, and grants.
- The component package can be independently verified by digest.
- A runtime upgrade is covered by conformance tests.

## Phase 5: first system execution backend

### Purpose

Support arbitrary commands and the GHA compatibility path without weakening the
component tier.

### Changes in `wsr`

- Define a system backend interface from execution requirements in the IR.
- Implement one development backend for a simple `run:` step.
- Capture stdout, stderr, exit status, timeout, and resource usage.
- Mount the immutable source snapshot read-only and provide separate bounded
  writable scratch space.
- Deny network and secrets by default.
- Record the selected backend and granted capabilities in evidence.
- Keep system and component worker pools logically separate.

### Isolation decision gate

The first backend may use a local process or container for development, but it
must not be described as a secure multi-tenant production boundary. Before
running hostile remote workloads, decide and test whether the production
boundary is a microVM, VM, hardened container configuration, dedicated host, or
another mechanism.

### Exit gate

- A supported GHA `run:` step is planned into the system tier and executes in an
  ephemeral environment.
- Timeout, cancellation, filesystem isolation, and output limits are tested.
- Component jobs cannot silently fall back to ambient system execution.
- Security documentation distinguishes development and production isolation.

## Phase 6: local end-to-end runner

### Purpose

Combine planning, both execution tiers, and evidence before adding remote
orchestration.

### Changes in `wsr`

- Execute a small job DAG with dependency and failure propagation.
- Run one native component check and one system command from a GHA fixture.
- Add matrix expansion for the tested subset.
- Implement cancellation and deterministic final status aggregation.
- Expose compatibility fallback decisions in CLI output.
- Persist local logs, artifacts, and evidence by invocation identity.

### Exit gate

- The first fixture can run locally without invoking GitHub Actions.
- Every operation explains why it used component or system execution.
- Unsupported constructs still fail during planning.
- A failed dependency prevents downstream execution according to documented
  semantics.
- Repeated execution does not reuse stale results across different digests.

## Phase 7: GitHub App and remote vertical slice

### Purpose

Restore the integrated GitHub CI/CD experience while keeping execution and state
outside GitHub Actions.

### Prototype location

Start in `wsr` or a temporary prototype until the service protocol and
deployment boundary are proven. Do not turn the existing `.github/src/index.js`
profile generator into the adapter by default.

### Changes

- Define a provider-neutral `PipelineRequest`.
- Implement GitHub App authentication with minimum repository permissions.
- Receive selected push, pull request, and check rerun events.
- Verify webhook signatures and deduplicate deliveries.
- Fetch or authorize retrieval of the exact commit revision.
- Persist authoritative pipeline and invocation state outside GitHub.
- Schedule one component job and one system job remotely.
- Project state, summaries, annotations, and links through GitHub Checks.
- Reconcile missed or failed GitHub API updates asynchronously.
- Define behavior for forks before exposing secrets or privileged execution.

### Extraction gate

Extract the GitHub App/control plane or worker into a new repository only when it
has an independent deployment and a versioned protocol with `wsr`. Until then,
prefer workspace crates to reduce distributed-system overhead.

### Exit gate

- A GitHub event creates exactly one authoritative pipeline invocation despite
  duplicate delivery.
- GitHub displays queued, running, and final states without a GHA workflow run.
- Rerun requests produce a new traceable invocation.
- Temporary GitHub API failure does not lose internal state.
- No GitHub-hosted runner or Actions execution API is invoked.

## Phase 8: artifacts, caches, secrets, and policy

### Purpose

Add shared platform capabilities after the vertical slice establishes their
actual interfaces.

### Changes

- Add immutable artifact storage and digest verification.
- Add cache namespaces, exact key semantics, poisoning controls, quotas, and
  retention.
- Add a secret broker using short-lived, job-scoped grants.
- Add policy evaluation for capabilities, forks, protected branches, component
  trust, and execution backends.
- Separate log retention from evidence retention.
- Define audit events for grants, approvals, component resolution, execution,
  and artifact promotion.
- Add deployment only after artifact identity and promotion rules are defined.

### Exit gate

- Artifacts are promoted by digest rather than rebuilt implicitly.
- Cache and artifact contents are verified before consumption.
- Secrets are unavailable unless both plan and policy authorize them.
- Fork workflows cannot obtain protected credentials by construction.
- Policy decisions and granted capabilities are visible in evidence.

## Phase 9: compatibility and component expansion

### Purpose

Grow from a proven vertical slice using measured demand.

### Changes in `wsr`

- Expand GHA semantics fixture by fixture.
- Add native mappings only when behavior can be tested against the original
  action.
- Add Preview 3 support for async and streaming workloads only after a concrete
  need and toolchain conformance are demonstrated.
- Evaluate WASIX only for workloads that are materially simpler than their
  system-tier equivalent.
- Add platform and hardware schedulers as explicit worker capabilities.
- Add another provider only to validate that the IR is genuinely
  provider-neutral.

### Changes in `actions`

- Add reviewed components with immutable releases and conformance tests.
- Define signing, provenance, revocation, and deprecation processes.
- Keep catalog growth tied to real compatibility gaps and native use cases.

### Exit gate

- Each advertised GHA feature has fixtures and end-to-end tests.
- Native action mappings have behavioral compatibility tests.
- WASI versions and runtime support are visible in scheduling diagnostics.
- Unsupported behavior remains explicit after compatibility expansion.

## Cross-repository dependency order

```text
.github design and status policy
            |
            v
wsr inspection -> pipeline IR -> snapshots/evidence
            |                       |
            v                       v
     component host          system backend
            |                       |
            +-----------+-----------+
                        v
                local vertical slice
                        |
                        v
          GitHub App + remote orchestration
                        |
                        v
          shared artifacts/secrets/policy

actions first component
  depends on: WIT contract + conformance harness in wsr

cargo-xdist
  remains independent; optional future external workload only
```

## Data migration

There is currently no production pipeline database, artifact store, cache, or
component registry to migrate. Early file formats should therefore be treated
as replaceable until explicitly versioned.

When persistent state is introduced:

- give every stored schema an explicit version;
- support forward migration before removing old readers;
- retain original GHA source and translation diagnostics for reproducibility;
- never mutate content-addressed snapshots or artifacts in place;
- distinguish user-visible pipeline identity from individual retry or rerun
  invocation identity;
- document retention and deletion separately for logs, artifacts, caches, and
  evidence.

## Compatibility migration policy

Existing workflow files should remain unchanged during initial adoption. The
compatibility frontend reads `.github/workflows/*.yml` and reports whether each
construct is native, emulated, a system fallback, or unsupported.

A native ectorial format should not be introduced until the pipeline IR and at
least one complete vertical slice are stable. When introduced:

- provide a generated migration preview from GHA YAML;
- preserve comments or report when they cannot be preserved;
- show semantic differences before writing files;
- never delete or rewrite GHA workflows without explicit user action;
- allow compatibility and native pipelines to coexist during migration;
- keep native format concepts provider-neutral.

The migration is successful even if some workflows remain on the system tier.
The goal is correct least-privilege dispatch, not maximizing the percentage of
steps labeled as WebAssembly.

## Assumptions

- `wsr` remains the core product and initial implementation repository.
- The current workspace restructuring in `wsr` is intentional and will be
  stabilized before architecture work builds on it.
- GitHub is the first required provider and primary CI/CD monitoring surface.
- GitHub Actions YAML is the first compatibility language.
- The Rust-template CI fixture remains the first compatibility target.
- A modular monolith is adequate until remote control-plane and worker
  deployments prove separate lifecycle requirements.
- WASI Preview 2 is the initial stable component baseline unless an experiment
  records a stronger reason to start with Preview 3.
- At least one system execution backend is required for meaningful GHA
  compatibility.
- `actions` is a curated native component catalog, not a mirror of the GitHub
  Actions marketplace.
- `cargo-xdist` remains independent from the core product architecture.
- No production user data or persistent CI/CD state currently requires
  migration.
- Existing uncommitted repository changes are outside this document's scope and
  should not be overwritten by migration work.

## Constraints

- The project is pre-alpha and does not yet have workflow execution behavior to
  preserve.
- Public documentation must distinguish **Implemented**, **Next**, and
  **Planned** capabilities.
- Full GitHub Actions compatibility is too broad to use as an initial milestone.
- GHA semantics can depend on runner images and implementation behavior outside
  the YAML schema.
- WebAssembly cannot faithfully provide all POSIX, container, macOS, kernel,
  service, or hardware semantics.
- WebAssembly isolation still requires secure host interfaces, resource limits,
  runtime maintenance, and possibly outer isolation.
- Containers alone may be insufficient for hostile multi-tenant workloads.
- GitHub APIs introduce rate limits, retries, outages, permissions, and
  provider-specific fork behavior.
- Rich GitHub Checks integration requires a GitHub App and appropriate
  permissions.
- Remote execution creates operational requirements for scheduling, storage,
  networking, credentials, observability, and incident response.
- Creating many repositories early would increase release and protocol overhead
  before boundaries are understood.
- Specialized macOS and hardware workers cannot be treated as generic
  WebAssembly or Linux capacity.

## Decisions required before production

- Supported GHA subset and compatibility versioning policy.
- Native pipeline format, if any, and its relationship to the IR.
- Initial WebAssembly runtime and runtime abstraction boundary.
- Stable WIT world and component version-negotiation policy.
- Production system isolation backend.
- Control-plane and worker deployment topology.
- GitHub App permissions, event subscriptions, and fork policy.
- Source snapshot normalization rules.
- Artifact, cache, log, and evidence storage and retention.
- Secret broker and approval model.
- Component signing, provenance, review, and revocation policy.
- Multi-tenancy model and threat model.
- Deployment and artifact promotion model.
- Repository extraction criteria and ownership.

## Migration-level acceptance criteria

The migration reaches the target architecture when:

- `wsr` translates the documented GHA subset into a provider-neutral plan;
- unsupported constructs fail during planning with actionable diagnostics;
- source inputs are immutable and identified by digest;
- one native component validation executes locally and remotely under explicit
  capabilities;
- one arbitrary command executes through an ephemeral system backend;
- both executions produce structured evidence and immutable artifact identities;
- GitHub events trigger authoritative external pipeline invocations;
- GitHub Checks displays status, summaries, annotations, and rerun controls;
- no execution depends on GitHub Actions or GitHub-hosted runners;
- duplicate webhooks and temporary GitHub API failure are handled idempotently;
- secrets and network access are denied unless explicitly authorized;
- every operation records its validation plane, execution tier, backend, and
  capability grants;
- repository documentation accurately distinguishes implemented and planned
  behavior;
- `actions` publishes only components conforming to the versioned platform
  contract;
- `cargo-xdist` remains usable independently of private `wsr` internals.

## Immediate next change

The next implementation change should remain narrower than this migration plan:

1. Stabilize the current `wsr` workspace and tests.
2. Add a deterministic inspection result for the existing Rust-template fixture.
3. Report `run:`, `uses:`, matrix, dependency, and unsupported constructs.
4. Do not execute workflow steps yet.

That increment validates the compatibility boundary required by every later
phase without prematurely selecting a runtime, service topology, or repository
split.
