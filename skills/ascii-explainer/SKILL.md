---
name: ascii-explainer
description: Explain concepts, workflows, architecture, algorithms, data layouts, and trade-offs with clear ASCII text diagrams. Use when the user asks for ASCII, text diagrams, or an explanation where relationships, boundaries, or changes matter. Do not force a diagram for a simple fact or a question one sentence can answer. Follow the user's choice if they request another format.
---

# ASCII Explainer

Help the reader answer a concrete question with a copyable text diagram. By default, deliver directly in chat with brief Chinese explanations; follow the user's language when different.

## Frame the Explanation

- Identify what the reader must understand: what connects, what changes, what comes first, where a boundary lies, or why a conclusion follows. Choose a representation for that question.
- State the main point briefly. Let the diagram show the relationships, then add the assumptions, exceptions, or reading instructions needed to understand it. Keep a concise textual takeaway so the conclusion does not depend on visually tracing the diagram. Do not narrate every line.
- For existing systems, use relevant code, specifications, or supplied facts. Distinguish observed behavior, possible behavior, proposals, and unknowns. A workflow diagram is not evidence that the workflow ran successfully.
- Establish only the scope that matters: viewpoint, participants, initial state, units, and simplifying assumptions. Label a worked example as an example; it does not prove all cases.

## Choose a Representation

| Reader's question | Useful representation | Preserve |
| --- | --- | --- |
| What belongs to what? | Tree or containment | Ownership versus reference; shared nodes |
| Who interacts or transforms data? | Labeled graph or typed pipeline | Edge meaning, data types, ports, boundaries |
| What happens next or on failure? | Flow or state transitions | Conditions, termination, retries, recovery |
| What must happen before what? | Dependency graph | Partial order; do not imply one execution schedule |
| How can these operations interleave? | Sequence lanes or event table | Participants, local order, synchronization |
| What changed? | Before/after snapshots | Stable identities, same viewpoint and scale |
| Which region or rule takes effect? | Aligned ranges and effective view | Priority scope, overlap, gaps, fallback |
| How is data laid out? | Indexed cells or bit/byte fields | Widths, offsets, units, padding, boundaries |
| Why is this step valid or wrong? | Aligned candidates or caret annotations | Exact mismatch, preconditions, counterexample |
| How do options or quantities compare? | Matrix, interval, or small bar chart | Common criteria, units, scale, uncertainty |

Use the smallest representation that answers the question. A table, annotation, or two snapshots may work better than boxes. For exact coverage, field boundaries, or resource schedules, make the checked interval/field/task table the diagram. Do not add a second spatial rendering of the same numbers unless the reader needs that spatial relationship. Use a proportional drawing when requested or necessary, and verify its cells against the table. For other dense topics, an overview and one useful detail may help; keep identifiers consistent.

Read the relevant section of [references/patterns.md](references/patterns.md) when you need a concrete layout or a check for one of these cases. Do not load or reproduce the whole catalog for a simple explanation.

## Preserve the Meaning

- Give each edge one clear meaning. Label calls, data, ownership, or ordering when they could be confused. Separate views when a single arrow style would mean several things. Structure order need not equal execution order.
- Keep object identifiers stable across views. Repeating a node for layout must be marked as a reference to the same object. Do not turn a shared object into several copies or an alias into ownership.
- Label exclusive branch conditions. Mark parallel work explicitly, and say whether a join waits for all, any, or a specified subset. Show failure, timeout, cleanup, or cancellation only when relevant; do not invent their behavior.
- Give loops a return target and an exit condition. Distinguish a retry budget from unlimited repetition. If crossings obscure a loop, use a labeled back-reference.
- In concurrent explanations, distinguish a possible trace from a guarantee. Side-by-side placement does not establish simultaneity or causality. Distinguish submitting work, finishing it, acknowledging it, and making it durable when that distinction affects the result.
- State whether lengths and positions encode quantities. For layouts and ranges, specify units, index origin, and inclusive/exclusive endpoints as needed. Show byte order only when established. A drawing's left-to-right order does not establish endianness.
- Define local symbols such as `.`, `?`, or `...`. Keep unknown, absent, zero, and omitted distinct. State consequential omissions; retain the detail that supports the conclusion.

## Make the Text Portable

- Use fenced `text` blocks, spaces instead of tabs, and ASCII lines/arrows such as `+ - | / \ > <`. Avoid Unicode drawing characters, emoji, Mermaid, and color dependencies by default. If strict ASCII is requested, use ASCII labels too.
- Use short labels. Chinese labels are suitable for simple vertical diagrams; for dense alignment use English identifiers and explain them outside. Count display columns, not bytes or string length. Do not assume mixed scripts have equal width.
- Aim for about 80 display columns or the user's narrower limit. Split, rotate, or simplify a wide diagram; do not wrap it through a connector. Put long labels in a nearby key.
- Avoid crossings. Make junctions and arrowheads unambiguous, and connect to the intended node or port. Place caret markers directly under the characters they annotate. Keep equal-scale axes evenly spaced.
- Prefer plain, direct sentences and consistent terms. Use one term for one concept. Do not claim compliance with a controlled-language standard unless it has been checked.

## Check Before Delivery

For exact ranges, field layouts, or resource schedules, read [references/checks.md](references/checks.md) and run the bundled `scripts/check.py` on a temporary JSON model transcribed from the source. It computes coverage and field offsets, validates proposed schedules, and renders aligned ASCII tables. Keep scenario variants separate. Compare the structured input with the source before trusting a pass.

Use the returned tables unchanged in the answer; explain them in the user's language outside the blocks. Run the checker again with `--answer` on the final draft to detect changed, omitted, extra, or misaligned blocks. Correct failures against the source and rerun. Do not hand-redraw the same checked data. Review prose against the computed facts; table verification does not validate prose. A feasible schedule is not an optimality proof unless the bound is reached or a separate proof is given. If tools are unavailable or the model cannot express the source semantics, disclose the unverified part rather than claiming a pass.

Also do two separate passes, scaled to the explanation:

1. **Semantic check:** Compare the diagram with the source, prose, and numbers. Trace one relevant input, object, or event through it. Check a boundary or failure case if it could change the conclusion. Check widths, counts, ordering, and conditions for the chosen representation. If evidence conflicts, resolve or disclose the conflict instead of silently copying the diagram.
2. **Visual check:** Read the exact monospaced block. Follow every connector to its endpoint; check marker positions, label alignment, junctions, and width. After an edit, recheck adjacent lines and related views. Correct geometry does not prove correct behavior. Conversely, correct prose does not repair a wrong diagram. If precise alignment is uncertain, replace the spatial drawing with an explicit interval or field table rather than leaving approximate markers.

Remove a diagram if it adds no useful relationship beyond the sentence. Formatting alone needs no tools; use tools to verify specific implementations, changing facts, or exact arithmetic when the task requires it.

This skill supports explanations and temporary calculation inputs. It does not authorize unrelated implementation, installation, or publication.
