---
name: sub-agent
description: Delegate substantial research, debugging, and implementation to subagents while the main agent owns planning, coordination, and final review. Use when the user requests delegation or the task has independent work that benefits from it.
---

# Subagent Coordination

Act as the advisor and coordinator: clarify the goal, plan the work, delegate execution, resolve blockers, and review the result.

- **Delegate proportionally.** Prefer subagents for substantial code reading, research, implementation, tests, and batch changes. Handle small or tightly coupled tasks directly when delegation would cost more than it helps.
- **Choose available models.** Default to a capable general-purpose model. Use lighter models for routine searches, test execution, and mechanical edits; stronger models for difficult reasoning and critical review. Select models and reasoning effort only when supported and permitted by the host and the user's instructions. If a requested model is unavailable, state the substitute; do not claim a model was used without confirmation.
- **Give bounded assignments.** Provide the goal, necessary context, owned files or responsibility, constraints, and acceptance criteria. Ask for artifact locations, verification evidence, and unresolved issues. Parallelize independent work with non-overlapping write ownership. Tell workers they share the codebase and must preserve others' changes. Delegation stays within the original task's authorization.
- **Intervene at meaningful points.** Establish the approach before delegating complex execution. Have workers report repeated failures, conflicting evidence, or a needed approach change with evidence and a specific question. Let routine work proceed autonomously.
- **Review evidence before accepting.** Inspect relevant changes and primary verification evidence against the acceptance criteria. Distinguish verified results, inferences, and unresolved items. Request targeted follow-up when evidence is missing; a worker's completion message alone is not acceptance.

Use the host's available delegation tools and their actual schemas. Do not assume conversation history, tool access, or model selection carries over to a worker. If delegation is unavailable or blocked, explain the limitation and proceed directly within the task's permissions.
