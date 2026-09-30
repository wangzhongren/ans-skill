# Common Framework Code and Resources

Use with role-card.md's Required reading. These rules retain the global mutation and architectural boundaries.

### One `common/` for Helpers and Framework Code

Use `src/common/` in a new five-layer project. It combines small utilities and supporting framework components; do not create a separate `utils/`. It is a supporting directory, not a sixth layer. Existing projects keep their current paths until a directory/ownership migration is explicitly accepted; do not silently move old utilities or add a competing copy.

```text
src/common/
  <role-id>/     # This role's private helpers and framework components
  shared/        # Cross-role components implemented by the project management role
```

1. **Role-local space.** Each capability role owns its accepted `common/<role-id>/` subtree and corresponding test scope. Within an approved task it may add, split, rename or remove internal files without requesting a boundary change for every filename. Record actual changes and update affected tests and feature/module documentation. Other roles do not import or edit this private subtree. Directory permission does not approve unrelated features, public-contract changes or edits outside that subtree.
2. **Shared space.** The project management role is the sole writer of `common/shared/`, its dedicated tests and the shared-component document. A capability role proposes a reuse need; the project role designs and implements the shared component and coordinates caller changes. It does not edit callers owned by other roles. The built-in ANS Governance role handles any ownership or permission changes.
3. **What belongs here.** Examples include encoding helpers, reusable validation mechanisms, result handling and in-memory framework support. A clear current purpose and interface can justify placement with one caller; two calls are not a hard threshold. Check existing components before adding another. Do not invent extension points merely because the directory exists.
4. **What stays in the layers.** Business decisions stay in Service, feature orchestration in Pipeline, infrastructure effects in Provider, and domain data contracts/invariants in Model. `common/` must not import or invoke the operational layers, including indirectly through callbacks used to hide orchestration. Domain types remain read-only Model dependencies under existing rules. A helper directory is not permission to skip a layer.
5. **Dependency direction.** A role's layers may use their own common code and declared shared entry points; private common code may use shared code. Shared code must not depend on a role's private common directory. Keep these dependencies acyclic. Cross-role reuse of business capabilities still goes through their owning layer's public entry; it does not automatically move into `shared/`.

### Shared-Component Document

The project management role maintains `docs/architecture/shared-components.md` inside its own role directory. Governance grants its actual path along with `common/shared/` and a dedicated test directory such as `test/<project-role-id>/shared/`. This is the current reuse catalog, separate from dated change/design history. Use clear prose and one entry per component:

| Field | Explain |
| --- | --- |
| Name and purpose | What problem it solves and why sharing helps |
| Code and public entry | Actual paths and supported entry points |
| Owner and users | Project management role as maintainer; current consumer roles and caller locations; mark planned users explicitly |
| Contract and example | Inputs, outputs, errors and a short real usage example |
| Tests and change impact | Corresponding tests, affected consumers and compatibility concerns |

Cross-role reuse follows this sequence: a role reports the need → project management writes a design and identifies consumers → the customer confirms the document and authorizes implementation → project management implements and tests `shared/` → it arranges each consumer's integration → affected tests run → the catalog, relevant feature flows/history and project architecture are updated. Reuse existing consent for the same version and scope. Do not leave two independently maintained copies after an approved extraction; each original owner updates its own caller and obsolete implementation.

Changes in shared behavior invalidate affected caller evidence. Frozen files and existing authorization rules still apply. Document each shared component once in the project role's catalog and contract; consumers link to it from their feature documents instead of copying definitions.

### Resources in `resource`

Use the root `resource/` folder for non-code assets such as templates, images, text files, and static reference data. Like `common`, it is a supporting directory, not an additional architectural layer, and does not require `abstract/`, `impl/`, `public/`, or a public entry module.

- Grow purpose-named subdirectories as actual assets require, such as `resource/templates/`, `resource/images/`, or `resource/data/`. Search existing resources before adding duplicates; preserve authoritative generated assets and their source workflow.
- Keep executable business logic and capability implementations in their owning layers. Model remains the owner of data contracts and validation; placing data in `resource/` does not make it a Model definition or grant it execution authority.
- Build-time or bundled static asset references may be used by their consuming layers without becoming operational calls. Runtime filesystem or network loading belongs to Provider; higher layers obtain resource-backed results through the existing adjacent-layer chain, never through direct loading or a `common` workaround.
- Include resource additions, edits, and required packaging or reference changes in the Mutation Contract. Verify format, referenced paths, and inclusion in the built or packaged output where relevant, then exercise affected consumers when resource content changes behavior. Resource changes can invalidate dependent evidence just like code changes.
