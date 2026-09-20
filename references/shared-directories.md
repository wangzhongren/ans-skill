# Shared Helpers and Resources

Use with role-card.md's Required reading. These rules retain the global mutation and architectural boundaries.

### Reusable Functions in `utils`

Keep the five architectural categories above: Model, Provider, Service, Pipeline, and Interface. `utils` is a folder for reusable helper functions, not a sixth layer or a new architectural role.

- When functions can be reused across Providers, Services, or other components, place them in focused modules under `utils`, such as `utils/encoding` or `utils/collections`. Follow an existing equivalent directory convention when the repository already has one.
- A function with a clear general-purpose use, a single responsibility, and a well-defined interface may be placed in `utils` even with only one current call site, so later tasks can discover and reuse it. When two or more call sites share the same semantics, including error behavior, prefer considering a shared helper. Call count is a signal, not an eligibility threshold. Keep functions that only serve local logic and lack a clear general-purpose use in their original location; do not add abstractions for hypothetical future requirements. Do not move whole components into `utils` merely because they have multiple callers.
- Directory placement does not change architectural responsibility or grant capabilities. Business rules, Model invariants, external effects, and orchestration remain governed by their owning layer, including when implemented through helpers. Shared imports must not bypass the existing dependency or capability boundaries.
- On each task, search `utils` and the relevant existing components before writing equivalent functions. Inspect signatures, behavior, callers, and relevant tests, then reuse compatible implementations. Use purpose-specific module and function names so later tasks can find them from the repository rather than relying on conversation memory.
- Before extracting or modifying shared functions, include the helper files, necessary caller edits, and relevant test changes in the Mutation Contract. Apply the existing scope-expansion rules, validate affected caller paths, and invalidate affected evidence when shared behavior changes. Frozen helper files retain the same protection as other frozen artifacts.

For example, a Provider and a Service may share a string conversion function in `utils/encoding`. They remain a Provider and a Service; the helper folder does not add another architectural layer.

### Resources in `resource`

Use the root `resource/` folder for non-code assets such as templates, images, text files, and static reference data. Like `utils`, it is a supporting directory, not an additional architectural layer, and does not require `abstract/`, `impl/`, `public/`, or a public entry module.

- Grow purpose-named subdirectories as actual assets require, such as `resource/templates/`, `resource/images/`, or `resource/data/`. Search existing resources before adding duplicates; preserve authoritative generated assets and their source workflow.
- Keep executable business logic and capability implementations in their owning layers. Model remains the owner of data contracts and validation; placing data in `resource/` does not make it a Model definition or grant it execution authority.
- Build-time or bundled static asset references may be used by their consuming layers without becoming operational calls. Runtime filesystem or network loading belongs to Provider; higher layers obtain resource-backed results through the existing adjacent-layer chain, never through direct loading or a `utils` workaround.
- Include resource additions, edits, and required packaging or reference changes in the Mutation Contract. Verify format, referenced paths, and inclusion in the built or packaged output where relevant, then exercise affected consumers when resource content changes behavior. Resource changes can invalidate dependent evidence just like code changes.
