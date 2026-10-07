> Historical unpublished draft, preserved during the October 7, 2026 documentation reconciliation.
> This is not current status, policy, or an executable migration plan. References and commands
> describe the original June-era context and may refer to deleted repositories or old paths.
> Use the active [organization overview](../../../README.md) and
> [WSR decision record](https://github.com/ectorial/wsr/blob/main/PLAN.md) instead.

# ectorial CI/CD system design

## Status

This document records the current design direction for ectorial's planned CI/CD
system. Unless identified as **Implemented**, everything here is **Planned** and
may change as the design is validated.

Current implementation status remains described by `ARCHITECTURE.md` and
`ROADMAP.md`. At the time of writing, `wsr` provides an early GitHub Actions
workflow parser and supporting CLI scaffolding; it does not implement the
execution architecture described below.

## Problem statement

GitHub Actions combines several concerns:

- a workflow language;
- event handling;
- orchestration and scheduling;
- arbitrary code execution on runners;
- artifacts, caches, secrets, and deployment controls;
- CI/CD monitoring inside GitHub.

The goal is to replace GitHub Actions as the orchestration and execution system
without losing GitHub's integrated developer experience. Developers should be
able to trigger, monitor, diagnose, rerun, and enforce pipelines from GitHub,
while pipeline execution remains independent of GitHub Actions.

The design also distinguishes two kinds of validation:

- **Source plane:** validates an immutable source snapshot without executing
  repository-controlled code. Examples include trusted formatting, structural
  linting, policy evaluation, dependency inspection, and secret scanning.
- **Runtime plane:** validates behavior by executing repository-controlled code
  or tools influenced by the repository. Examples include compilation, tests,
  integration environments, and hardware compatibility checks.

This is a trust boundary, not merely a distinction between checks that read
files and checks that run tests. A compiler, formatter, linter, configuration
loader, package manager, or plugin can execute repository-controlled code and
therefore may belong in the runtime plane.

## Design goals

- Remove GitHub Actions as an execution and orchestration dependency.
- Retain GitHub as the initial source provider and primary CI/CD monitoring
  surface.
- Accept a documented subset of GitHub Actions YAML with minimal migration
  effort.
- Provide a native, typed pipeline model independent of GitHub concepts.
- Run each operation on the least-privileged backend capable of satisfying its
  requirements.
- Make source, artifacts, components, policies, and results content-addressable
  where practical.
- Provide consistent local and remote source validation.
- Produce structured evidence that can be projected into GitHub Checks.
- Make unsupported compatibility behavior explicit rather than silently
  changing workflow semantics.

## Non-goals

- Reimplement every GitHub Actions feature before the first useful release.
- Treat GitHub Actions YAML as the platform's internal representation.
- Run every existing CI/CD workload in WebAssembly.
- Emulate a complete Linux or Docker environment through WASI.
- Trust developer-local results automatically for protected branches.
- Claim that WebAssembly alone is a complete security boundary.
- Make performance or security claims before they are measured and tested.

## Terminology

- **Pipeline frontend:** parses an external pipeline language and translates it
  into the internal representation.
- **Pipeline IR:** provider-neutral, typed internal representation used for
  planning, policy, and scheduling.
- **Component execution:** WebAssembly Component Model execution with explicit
  capabilities.
- **System execution:** arbitrary commands or actions executed in an ephemeral
  container, microVM, VM, native host, or hardware worker.
- **Evidence:** structured result tied to exact input, tool, policy, and
  environment identities.
- **Projection:** the representation of authoritative internal state in an
  external UI such as GitHub Checks.

## Proposed architecture

```text
GitHub
  repositories, identity, pull requests, webhooks, Checks UI
       |
       v
GitHub App adapter
  authentication, event translation, result projection, reconciliation
       |
       v
Control plane
  pipeline frontends -> pipeline IR -> policy -> planner -> scheduler
       |                                      |
       |                                      +-> metadata and evidence store
       |                                      +-> content-addressed storage
       v
Execution layer
  +--------------------------------+  +----------------------------------+
  | Tier 1: component execution    |  | Tier 2: system execution         |
  | Wasm + WASI + Component Model  |  | containers, microVMs, VMs, hosts |
  | typed and capability-limited   |  | arbitrary system behavior        |
  +--------------------------------+  +----------------------------------+
       |                                      |
       +------------------+-------------------+
                          v
                 logs, artifacts, evidence
                          |
                          v
                 GitHub Checks projection
```

The source/runtime planes and execution tiers are related but orthogonal:

- Trusted source checks should normally use component execution.
- Portable runtime tests may also use component execution.
- Source-oriented tools that execute repository code require system execution.
- Platform, service, kernel, and hardware tests require system execution.

## GitHub integration boundary

GitHub remains mandatory for the initial product experience, but it does not own
pipeline execution or authoritative state.

The GitHub App adapter is responsible for:

- receiving push, pull request, check rerun, and requested-action events;
- authenticating repository access with minimum required permissions;
- translating GitHub events into provider-neutral pipeline requests;
- retrieving or authorizing retrieval of an exact commit;
- publishing queued, running, successful, failed, cancelled, and action-required
  check states;
- publishing summaries and source annotations;
- linking to detailed logs and artifacts;
- reconciling internal state after webhook retries, API failures, or rate limits.

The platform database remains authoritative. GitHub Checks is a projection. All
webhook handling and check updates must therefore be idempotent.

A provider-neutral request should resemble:

```text
PipelineRequest
  repository URI
  source provider
  revision
  target revision, if any
  event kind
  actor identity
  credentials reference
```

Adding another source provider should require a new adapter, not a change to the
pipeline engine.

## GitHub Actions compatibility

GitHub Actions YAML is an adoption frontend, not the native execution model:

```text
.github/workflows/*.yml
        |
        v
GHA compatibility frontend
  parse -> validate -> classify -> translate
        |
        v
provider-neutral pipeline IR
```

Compatibility includes more than YAML syntax. The frontend may need to model:

- expressions and contexts;
- matrices, dependencies, conditions, and outputs;
- environment and secret propagation;
- reusable and composite workflows;
- shell and platform defaults;
- caches, artifacts, services, environments, permissions, and concurrency;
- JavaScript, Docker, and third-party actions.

Every construct must be classified as one of:

- **Native:** translated into a typed platform operation or component.
- **Emulated:** executed with documented GitHub Actions-compatible semantics.
- **System fallback:** delegated to the system execution tier.
- **Unsupported:** rejected with an actionable compatibility diagnostic.

For example:

```text
GHA construct                 Likely execution
expression or matrix          control-plane IR or component
known native action           component
known source analyzer         component
run: shell command            system execution
JavaScript/composite action   system execution unless mapped safely
Docker action                 system execution
service container             system execution
GPU or platform validation    matching hardware/system worker
```

The compatibility promise should name a tested subset. Full, seamless GitHub
Actions compatibility would require reproducing much of the Actions runner and
must not be implied before it exists.

## Pipeline IR and planning

The pipeline IR must not contain GitHub-specific execution semantics. It should
represent at least:

- immutable inputs and their digests;
- validation type and dependencies;
- typed inputs and outputs;
- execution requirements;
- capability requests;
- environment and hardware constraints;
- cache and artifact operations;
- timeout, retry, and concurrency policy;
- secret references rather than secret values;
- compatibility origin and translation diagnostics.

Planning must happen before scheduling. The planner expands matrices, resolves
components and immutable versions, evaluates static policy, classifies execution
tiers, and reports unsupported behavior. Ambiguous work defaults to system
execution rather than being incorrectly treated as safe.

## Tier 1: component execution

The native execution model uses WebAssembly, WASI, and the Component Model.
Components expose typed WIT interfaces and receive no ambient authority.

Likely component workloads include:

- source analyzers and format checks;
- organization and repository policy;
- dependency, license, and secret inspection;
- condition and matrix extensions;
- result aggregation and annotation formatting;
- artifact transformations;
- portable unit tests and services;
- controlled cache, artifact, and HTTP clients.

The host provides narrow interfaces for source snapshots, scratch storage,
logging, evidence, artifacts, caches, secrets, and controlled networking. A
platform-owned world could resemble:

```wit
world pipeline-component {
    import source-store;
    import scratch-store;
    import log;
    import cache;
    import artifacts;
    import secrets;
    import controlled-http;

    export validation;
}
```

WIT interfaces are public compatibility contracts. They require explicit
versioning, deprecation, and migration policies.

Component execution still requires defense in depth: resource metering,
interruption, memory limits, capability enforcement, runtime patching, and
possibly an outer process or microVM boundary for hostile multi-tenant work.

### WASI technology policy

- **WASI Preview 1:** compatibility for existing command-oriented modules; not
  the preferred public extension API.
- **WASI Preview 2:** conservative baseline for stable component and analyzer
  interfaces because it provides WIT and the Component Model.
- **WASI Preview 3:** candidate for asynchronous and streaming components such
  as logs, artifacts, HTTP, caches, and long-running agents. Adoption should be
  gated on runtime and language-toolchain maturity.
- **WASIX:** optional backend for selected POSIX-oriented WebAssembly programs.
  It must not define the pipeline IR or portable component contract because it
  expands the process, thread, signal, and socket surface and introduces tighter
  runtime ecosystem coupling.

The runtime and binding generator must agree on WIT package versions. Runtime
support should be represented as worker capabilities so the scheduler does not
send incompatible components to a worker.

## Tier 2: system execution

System execution handles workloads that require arbitrary operating-system
behavior:

- shell commands and existing GitHub Actions;
- compilers, package managers, and build scripts;
- JavaScript and Docker actions;
- service containers and integration environments;
- kernel-, operating-system-, architecture-, or hardware-specific tests;
- Xcode/macOS, GPU, embedded, and other native validation.

System execution is untrusted by default and receives explicit resource,
network, secret, and time limits. Containers alone share the host kernel;
multi-tenant or high-risk workloads should use stronger isolation such as
ephemeral microVMs. Native and hardware workers require equivalent lifecycle and
credential controls even when virtualization is unavailable.

Tier 2 is not a lower-quality failure mode. It is the correct backend for work
whose required semantics cannot be represented faithfully by WASI.

## Source snapshots and local execution

The mutable working tree is captured into an immutable, content-addressed source
snapshot. Validation results are keyed by at least:

- source digest;
- component or tool digest;
- policy digest;
- declared capabilities;
- relevant environment identity.

The local agent can execute component checks against the same snapshot and
component digests used remotely. This gives fast feedback and local/remote
parity. Locality does not establish trust: protected branches may require
central re-execution or evidence from an enrolled, attested machine.

Remote runtime execution must consume the exact snapshot that was analyzed,
not a later checkout of a mutable branch.

## Evidence, artifacts, and state

Every validation should produce structured evidence in addition to logs:

```text
ValidationEvidence
  pipeline and invocation identity
  source digest
  component/tool digest
  policy digest
  granted capabilities
  execution environment identity
  findings and annotations
  output artifact digests
  conclusion
```

Artifacts should be immutable and content-addressed. Promotion and deployment
should consume already-validated artifact digests rather than rebuilding from
source.

An initial internal-to-GitHub state projection may be:

```text
Internal state          GitHub check state
created                 queued
scheduled               queued
executing               in_progress
passed                  completed/success
failed                  completed/failure
cancelled               completed/cancelled
infrastructure failure  completed/action_required
```

## Security model

The design assumes repository contents, workflow definitions, third-party
actions, dependencies, build scripts, and runtime commands are untrusted.

Required controls include:

- immutable input identity;
- least-privilege GitHub App permissions;
- capability-based component host APIs;
- deny-by-default network and secret access;
- short-lived, scoped credentials from a secret broker;
- execution time, CPU, memory, storage, and output limits;
- separate worker pools and trust domains for component and system execution;
- signed components and verified content digests;
- provenance, audit logs, and evidence retention;
- protection against artifact and cache poisoning;
- explicit policy for forked pull requests;
- runtime and base-image vulnerability response.

"WASM-native" must not be presented as synonymous with "safe." Safety depends
on the runtime, host interfaces, capability grants, resource limits, outer
isolation, and operational controls.

## Assumptions

- GitHub is the initial required source provider and primary monitoring UI.
- GitHub Apps, webhooks, and the Checks API remain available for external CI
  integrations.
- Users value seeing source changes and CI/CD state in the same GitHub workflow.
- Existing GitHub Actions YAML materially reduces migration friction.
- A documented compatibility subset is acceptable before complete coverage.
- Most source snapshots and component outputs can be identified by content
  digest.
- Trusted platform analyzers can be packaged as signed components with stable
  WIT interfaces.
- Some runtime validation can be compiled to WebAssembly, but substantial
  existing CI workloads require POSIX, containers, VMs, or physical hardware.
- Local checks are useful for feedback even when central verification remains
  authoritative.
- The scheduler can select workers using declared OS, architecture, hardware,
  WASI version, runtime, and isolation capabilities.
- The `ectorial/actions` repository may eventually host native action
  components, but its format and trust policy are not yet defined.

## Constraints

- GitHub API rate limits, outages, webhook retries, permissions, and fork
  behavior must not corrupt authoritative pipeline state.
- Check creation and rich result reporting require an appropriately permissioned
  GitHub App.
- GitHub Actions behavior is large, evolving, and partially coupled to runner
  images and implementation details.
- Arbitrary `run:` steps and third-party actions cannot be safely translated
  into source-plane checks by default.
- WASI and Component Model support varies across runtimes, versions, languages,
  and binding generators.
- WASI does not provide complete Linux, Docker, macOS, kernel, or hardware
  semantics.
- WASIX broadens compatibility but also broadens authority and may constrain
  runtime choice.
- Containers share the host kernel and are not always a sufficient isolation
  boundary for hostile multi-tenant execution.
- Native macOS and specialized hardware capacity will remain scarce and
  operationally different from generic workers.
- Secrets cannot safely enter untrusted fork workloads without an explicit
  policy and approval mechanism.
- Reproducibility is limited when tools access mutable networks, package
  registries, clocks, random sources, or external services.
- The project is pre-alpha; public documentation must distinguish implemented,
  next, and planned capabilities.

## Benefits of the proposed model

- Fast, dense execution for suitable component workloads.
- Typed interfaces and pre-execution pipeline validation.
- Explicit authority instead of ambient runner permissions.
- Consistent local and remote components.
- Portable native actions across supported hosts.
- Structured results rather than exit codes alone.
- GHA migration without making GHA semantics the internal architecture.
- Correct support for platform-specific workloads through system backends.

## Costs and risks

- Building and maintaining a correct GHA compatibility compiler is substantial.
- Two execution tiers increase scheduler, observability, and operations scope.
- Component SDK and WIT evolution can create ecosystem fragmentation.
- Debugging components may initially be less familiar than debugging shell jobs.
- Native action replacements require behavioral conformance testing.
- A component registry introduces signing, provenance, revocation, and supply
  chain responsibilities.
- Aggressive WASM-only positioning could reject important real-world workloads.
- Broad WASIX adoption could recreate a complex POSIX runner with weaker
  ecosystem portability.
- GitHub remains a product dependency for the initial integrated experience,
  even though GitHub Actions is removed as an execution dependency.

## Proposed delivery sequence

### Implemented

- Early `wsr` CLI and GitHub Actions workflow parsing scaffolding.
- Placeholder `ectorial/actions` repository.

### Next

1. Parse representative workflows into a normalized, inspectable plan.
2. Classify each workflow feature as native, emulated, system fallback, or
   unsupported.
3. Produce compatibility reports without executing workflows.
4. Define the minimum provider-neutral pipeline IR and execution requirement
   model.

### Planned

1. Implement a GitHub App adapter and idempotent internal state projection.
2. Define a minimal WIT world for one read-only source analyzer.
3. Execute that analyzer locally and remotely against the same source digest.
4. Add one ephemeral system backend for a simple `run:` job.
5. Publish both results as GitHub check runs.
6. Add evidence, artifact, cache, secret, and policy services incrementally.
7. Expand the tested GHA subset based on real workflow fixtures.

The first end-to-end milestone is:

```text
GitHub webhook
  -> exact source snapshot
  -> GHA compatibility planning
  -> one component source check
  -> one ephemeral system job
  -> structured evidence
  -> GitHub Checks result
```

## Success criteria

- Deleting `.github/workflows` after translating a pipeline into the native
  format does not affect execution semantics.
- No execution path invokes GitHub Actions or depends on a GitHub-hosted runner.
- A developer can monitor and rerun supported pipelines without leaving GitHub.
- The same component and source digests can be executed locally and remotely.
- Unsupported GHA constructs fail during planning with actionable diagnostics.
- Every scheduled operation records why its execution tier was selected.
- Tier 1 jobs receive only declared capabilities.
- Tier 2 jobs are ephemeral and constrained by explicit policy.
- GitHub outages or duplicate webhook delivery do not lose or duplicate
  authoritative pipeline executions.
- Another source provider could be added through an adapter without redesigning
  the pipeline IR or execution layer.

## Open questions

- What exact GHA subset defines the first compatibility milestone?
- Which GitHub events and App permissions are required for the first release?
- What is the minimum pipeline IR that supports both compatibility and native
  component pipelines?
- Which WIT interfaces belong in the first stable platform world?
- Is WASI Preview 2 the initial stable ABI, and what evidence would justify
  adopting Preview 3 for production components?
- Which runtime should be the first implementation, and how portable must the
  runtime abstraction be?
- Is WASIX worth supporting before the container/microVM compatibility backend
  is mature?
- What outer isolation is required for hostile component workloads?
- Which system backend provides the first acceptable balance of startup time,
  compatibility, isolation, and operating cost?
- How are local attestations established, and which policies may trust them?
- Where are logs, artifacts, caches, and evidence stored and retained?
- How are components signed, reviewed, revoked, and distributed?
- How will native action mappings be tested for behavioral compatibility with
  their GHA counterparts?
- What deployment model follows artifact validation, and should deployment be a
  separate trust plane?

## Decision summary

The current direction is:

> Build a component-native CI/CD system with GitHub-native monitoring and a
> GitHub Actions compatibility frontend. Execute typed, capability-constrained
> work through WebAssembly components, and isolate workloads requiring ambient
> operating-system behavior in ephemeral system sandboxes.

This direction is not a commitment to WASM-only execution or complete GitHub
Actions compatibility. Those would conflict with the system's compatibility and
platform-validation requirements.

## References

- [GitHub Checks API guide][github-checks]
- [WASI project](https://github.com/WebAssembly/WASI)
- [WASI 0.3 overview](https://wasi.dev/releases/wasi-p3)
- [WebAssembly Component Model](https://component-model.bytecodealliance.org/)
- [WASIX API reference](https://wasix.org/docs/api-reference/)

[github-checks]: https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks
