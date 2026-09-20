# Shared Architecture and Module Organization

Use with role-card.md's Required reading. These rules retain the global mutation and architectural boundaries.

### Five-Layer Source Tree

The source tree under `src/` follows the five operational layers as top-level directories. Every feature's code lives in the layer it belongs to — not in a feature-named directory.

```
src/
  interface/     HTTP, CLI, RPC, event, job, or GUI adapter
  pipelines/     sequencing, branching, retry, parallelism, composition
                   (may have subdirectories per capability, e.g., pipelines/render/)
  services/      business transformations
    abstract/      contracts and interfaces (one file per capability)
    public/        entry point — factory functions and type exports
    impl/          concrete implementations (one file or subdir per capability)
  providers/     infrastructure capabilities
    abstract/      contracts and interfaces (one file per capability)
    public/        entry point — factory functions and type exports
    impl/          concrete implementations (one file or subdir per capability)
  models/        shared schemas, types, value objects, invariants
                   (may have subdirectories per domain, e.g., models/physics/)

  Supporting directories at project root:
  test/          organized by role: role-owned, language-native test files
  utils/         shared helpers (no business logic)
  resource/      static assets
  docs/          design, feature, change, fix records
```

A capability (e.g., "physics") contributes files to multiple layers — `services/physics/` + `providers/physics/` — rather than owning its own top-level `physics/` directory.

**For existing projects:** Accept the current directory structure as-is. Section 1 lists the actual file paths. Do not propose a restructuring unless the task explicitly authorizes it.

### Layer Internal Structure

Service and Provider layers follow a three-part internal structure at the top level:

```
services/  (or providers/)
  abstract/      Contracts and interfaces. One file per capability.
                   Higher layers depend on these, never on impl/.
  public/        The designated public entry (language-specific). Exposes factory functions
                   and type references for all capabilities.
  impl/          Concrete implementations. One file or subdirectory per capability.
                   Not directly imported by higher layers.
```

A capability contributes its contract and implementation files, and exposes its API through the uniquely owned layer public entry. The entry may be a module in `public/` or a root facade exposing `public/`, depending on repository conventions; declare exactly which path external callers use.

Keep concrete classes internal. Construction and implementation selection obey the adjacent-layer rule. Public factories must not become service locators or expose lower-layer capability objects.

### Shared Contract and Public-Export Rules

The layer references linked from [SKILL.md](../SKILL.md) define which directories and entry points are required. Public entry filenames are language-dependent: `index.js` is a JavaScript option, not a cross-language requirement. Use the established package entry or facade mechanism for the project, with internal implementation symbols hidden. If the language cannot literally map these directory names (for example a reserved keyword), preserve the responsibilities using valid names and document the mapping. Do not create JavaScript files in another language solely to satisfy this convention. Internal subdivisions and supporting `utils/` and `resource/` folders do not add architectural layers. Folder conventions do not authorize unrelated repository migrations; include necessary moves and import changes in the Mutation Contract.

- Express contracts using appropriate language mechanisms such as interfaces, protocols, abstract base classes, or callable types. Specify inputs, outputs, errors, and relevant behavioral guarantees. Keep concrete infrastructure access and business execution out of abstractions. Multiple implementations may share a contract; do not create an abstract class for every file or private helper.
- Implementations import their own contracts directly from `abstract/`. Abstractions must not import implementations, facades, or root entry points, including through re-exports. Internal modules must not loop back through their own facade.
- For Provider and Service public entry points, explicitly expose only the supported API of the layer's own `public/`, using the language's package, module, header, or visibility mechanisms. Do not export directly from `impl/`, use wildcard exports, or put business logic in the export facade. The facade exposes supported operations, contracts where supported by the language, necessary data types, and factories returning the layer's own contract. Do not duplicate definitions or implementation logic.
- Keep concrete classes internal. Construction or injection and local implementation selection must obey the adjacent-layer rule. Public factories must not become service locators or expose lower-layer capability objects. Importing an entry point must not initialize external resources.
- Focused internal tests may inspect internals; production consumers and public API tests use the declared layer entry point. Changes to public exports or contracts follow authorization, compatibility, and evidence-invalidation rules.

### Separate Responsibility, Capability Reuse, and Call Direction

Make three distinct decisions. Responsibility determines module ownership; existing capability determines reuse; layer position determines the legal call path. Reusing an implementation means invoking its supported behavior, not adding new responsibilities to its module.

#### Projection 1: Responsibility Ownership

Map each requested behavior to its business concept or technical responsibility, contract, state/lifecycle, and reason to change. These properties establish the module boundary; layer count and file count do not.

| Relationship to existing behavior | Action |
| --- | --- |
| An existing capability already satisfies the requirement | Invoke it through its permitted entry point; leave its implementation unchanged |
| The requirement changes or repairs the behavior of an existing responsibility | Modify the module owning that responsibility and verify its affected contract |
| The requirement introduces an independent responsibility | Create a focused module for it, or use an existing module already owning that responsibility; reuse other capabilities through legal composition |

Apply the table separately to distinct behaviors in a compound task. Use actual semantics and independent reasons to change to distinguish a new responsibility from a variant of an existing one. Different state lifecycles or unrelated dependencies are supporting evidence; matching fields, shared code shape, line count, or a `switch` statement alone do not decide ownership. This judgment requires semantic review, not a fabricated automatic score.

A public facade may remain stable while exposing explicit operations backed by separate implementations. Public entry points and required Provider/Service subdivisions belong to the layer; do not recreate them for each feature. Extracted private helpers remain part of their component's responsibility and must not conceal independently orchestrated Services.

#### Projection 2: Permitted Dependency Edges

After identifying responsibility owners and reusable capabilities, connect them using the global adjacent-layer rule. A valid ownership split does not authorize upward, skipped-layer, or peer-component calls. Compose independent Services in Pipeline and retain the public-entry boundaries.

Reuse an existing path when it already provides the required contract. If a needed boundary is absent, add its smallest meaningful operation in the appropriate module. A single-Service Pipeline operation can own a workflow contract; it does not require a separate feature-named file. Do not add wrappers whose only purpose is to make every feature appear in every layer, and do not replace boundaries with a universal dispatcher or lower-layer API re-export.

The call graph need not visit all layers. A pure Service computation may return a Model value without a Provider; Interface may reject invalid input before invoking Pipeline. Execution ends where the owning responsibility is fulfilled unless it needs a lower-layer capability.

#### Example: Order Query and Export

If an order query capability already exists, adding order export does not make export logic part of the query module. If querying and export transformation are independent Service responsibilities, Pipeline invokes the query Service and passes its returned data to the export Service. Neither Service calls the other. Existing Interface/Pipeline operations may be reused when their contracts already fit; otherwise add only the missing operations in their owning modules. A compatible query bug fix, by contrast, changes the query implementation and need not create new caller files.

Review the responsibility mapping and dependency edges separately: the first detects unrelated logic collected in one owner; the second detects illegal calls. A candidate must satisfy both.

### Incremental Implementation Organization and Dependencies

Grow Provider and Service `impl/` modules according to current responsibilities and dependencies within the authorized task. Apply the same rules to optional `impl/` subdivisions in other layers. This is incremental code organization, not permission to generate speculative features or migrate unrelated modules.

- Inspect existing contracts, implementations, helpers, and callers first. Reuse a compatible implementation; add a module only for a distinct responsibility or an implementation strategy required by the task.
- Start with individual files. Introduce a purpose-named subdirectory when an implementation has several related files that benefit from being maintained together. Do not pre-create empty trees or organize modules by task number or development round.
- Before adding or changing dependency edges, identify the affected modules, their direct dependencies, and callers. Keep the affected module dependency graph directed and acyclic; directory nesting alone does not establish a valid dependency direction. Do not introduce cycles through imports, re-exports, public factories, or shared helpers. Existing cycles do not authorize an unrelated rewrite; report a blocking cycle and apply scope-expansion rules when necessary.
- Keep private helpers near the implementation they support. Move functions with a clear general-purpose use into `utils` according to its reuse rules. Do not move business orchestration into helpers to disguise a dependency between peer Services.
- Internal modules may collaborate within one component's responsibility. Cross-component dependencies must use permitted contracts and public entry points where defined, rather than importing another component's implementation internals. Composition of Services remains in Pipeline-equivalent code and all cross-layer calls obey the strict adjacent-layer rule.
- Adding or splitting an implementation does not automatically add a public capability. Reuse an existing contract when it fits; update `abstract/` and public exports only when the requested outcome requires a contract or exposure change, under the existing authorization rules.
- Include new files, moves, and necessary caller changes in the Mutation Contract. Implement and validate dependencies before their affected callers where practical, then verify affected execution paths and refresh invalidated evidence. Do not create a persistent dependency registry unless the repository already requires one.
