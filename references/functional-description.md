# Functional Description (功能描述)

A companion document to `boundary.md`. It contains architecture diagrams and key code locations — everything that is NOT the mutation whitelist. The role card lists which system features this role owns; each feature's current behavior belongs in a separate [`features/<feature-id>.md`](feature-point.md), not in one large role-level explanation.

For the role's cross-project workflow position and topic navigation, use [project-context.md](project-context.md). Link shared contracts rather than copying their definitions into either document.

## Structure

````markdown
# Functional Description: <Role Name>

## Architecture Diagram

<!-- Mermaid or ASCII diagram showing call flow, dependencies, and layers -->

```mermaid
flowchart LR
  A[Interface: api.js] --> B[Pipeline: game-loop.js]
  B --> C[Service: scene-manager.js]
  C --> D[Provider: database.js]
```

## Key Code Locations

| What | Where |
| --- | --- |
| Entry point | `src/interface/api.js:12` — `handleRequest()` |
| Core logic | `src/services/appointment.js:45` — `createAppointment()` |
| Provider call | `src/providers/database.js:22` — `DatabaseProvider.query()` |

## Detailed Explanation

### How the role's modules fit together

Explain the shared architecture and data handoffs here. Link each owned system feature's `features/<feature-id>.md` for its trigger, complete flow, branches and results.

### Ownership

| File | Layer | Permission |
| --- | --- | --- |
| `src/services/appointment.js` | Service | Exclusive |
| `src/providers/database.js` | Provider | Shared |

### Cross-Module Notes

Coordination points with other roles, shared contracts, and event schemas.

````

## Rules

- Updated by the owning role whenever the architecture changes.
- The assembly role does not need to read this file — it reads `api-spec.md` instead.
- Diagrams are required — use Mermaid for renderable diagrams, ASCII for simple flows.

## See also

- [Module boundary document](module-boundary.md)
- [API spec](api-spec.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
## Optional Interactive Walkthrough

When the user requests it, use [role-atlas.md](role-atlas.md) to turn described features into role-scoped overviews and source-anchored, declarative step sequences. Keep normal/error scenarios, assumptions and current-code discrepancies explicit. This does not automatically run on every implementation task.
