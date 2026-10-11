---
name: ascii-explainer
description: Explain concepts, business logic, workflows, system architecture, and differences between options with ASCII diagrams. Use when the user asks for ASCII, text diagrams, or clear relationships, or when a diagram would help explain a topic. Do not force a diagram for simple facts or questions that one sentence can answer. Follow the user's choice if they request another format.
---

# ASCII Explainer

Help users understand relationships and behavior through diagrams. By default, provide copyable text diagrams directly in chat with brief Chinese explanations. If the user uses another language, use that language instead.

## Organize the Explanation

- State the main point in one sentence, then expand it with a diagram. Let the diagram carry the explanation. Add prose only for key differences, constraints, and exceptions; do not repeat the diagram line by line.
- First identify the relationship the user needs to understand: composition, calls, data flow, sequence, state changes, or differences between options. Choose the diagram type that best shows it.
- For complex topics, start with an overview, then expand one important part. Do not pack every module and detail into one diagram.
- Base explanations of existing systems on known facts or relevant code. Clearly distinguish the current implementation, proposed changes, and unknowns. The existence of a workflow does not prove that it has run or passed acceptance checks.

## Choose a Diagram

| Topic | Preferred format |
| --- | --- |
| Concepts and composition | A tree, containment, or a few labeled relationships |
| Workflows and decisions | A flow in one direction, conditional branches, and clear joins or endpoints |
| Architecture and responsibilities | A layered or component diagram with clear boundaries and interfaces |
| Interactions between participants | A short swimlane or sequence diagram |
| Changes and choices | Before / After or side-by-side comparisons at the same level of detail |
| States and feedback | A state transition diagram with events, loops, and exit conditions |

Do not show every diagram type or follow a fixed template.

## Drawing Rules

- Put diagrams in fenced `text` code blocks. Use spaces for indentation, not tabs.
- Use ASCII characters for boxes, lines, and arrows, such as `+ - | / \ > <`. Do not use Unicode box-drawing characters, emoji, or Mermaid by default.
- Prioritize readable labels. Chinese labels work well in simple vertical diagrams. For complex alignment, use short English labels and explain them in Chinese outside the diagram. Do not assume that Chinese and English characters have the same display width.
- Aim for about 80 display columns or fewer. If a diagram is too wide, make it vertical, split it into two diagrams, or reduce the number of nodes. Do not rely on a smaller font.
- Give arrows a clear meaning, such as calls, data transfer, or state transitions. If the meaning could be unclear, label the line or add a short legend. Use each line style consistently within a diagram.
- Label conditions on mutually exclusive branches. Mark parallel branches as parallel. When several arrows converge, make clear whether the next step needs one incoming path or all incoming paths to finish.
- Mark where loops return and when they exit. Show errors, timeouts, recovery, or cleanup when they affect understanding; omit them otherwise.
- Preserve actual responsibilities, data ownership, and process or device boundaries. Do not invent components, dependencies, or guarantees to make a diagram symmetrical.

## Short Examples

To explain responsibilities:

```text
[UI] -- request --> [Runner] -- action --> [Device]
 |                     |
 |                     +-- evidence --> [Report]
 +---------------- read --------------------^
```

To explain retries, make the conditions visible:

```text
[Attempt] --> <Result?> -- success --> [Done]
    ^             |
    |             +-- retryable + budget left --+
    +-------------------------------------------+
                  |
                  +-- otherwise --> [Failed]
```

These examples show drawing techniques only. They are not facts about the system being explained or a required architecture.

## Check Before Delivery

Follow each arrow. Do its start, direction, condition, join, and endpoint make sense? Are node names consistent? Do the diagram and prose agree? If you omit details that affect the conclusion, state that in one sentence.

This skill is for explanations. It does not by itself authorize implementation, installation, publication, or the creation of extra files. Formatting a diagram alone does not require tools. Verify specific implementations or facts that may change when the task requires it.
