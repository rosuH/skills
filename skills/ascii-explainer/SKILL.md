---
name: ascii-explainer
description: Explain concepts, workflows, architecture, algorithms, data layouts, and trade-offs with clear ASCII text diagrams. Use when the user asks for ASCII, text diagrams, or an explanation where relationships, boundaries, or changes matter. Do not force a diagram for a simple fact or a question one sentence can answer. Follow the user's choice if they request another format.
---

# ASCII Explainer

Help the reader understand a concrete question through a copyable text diagram. Follow the user's language and format preferences.

## Find the Visual Idea

Start with the relationship the reader needs to see. Choose, invent, or combine representations to make it visible. These are starting points, not a required menu:

| What needs to become clear? | Ideas to explore |
| --- | --- |
| Membership, ownership, or shared objects | Trees, containment, labeled references |
| Interaction or transformation | Labeled graphs, pipelines, message lanes |
| Decisions, failure, or repetition | Branches, state transitions, loops, back-references |
| Order, concurrency, or waiting | Dependency graphs, event traces, timelines |
| Change over time | Before/after views, snapshots, a short sequence of frames |
| Extent, boundaries, or layout | Overlays, range strips, indexed cells, exploded fields |
| A mistake or a reasoning step | Carets, aligned candidates, counterexamples |
| Differences or quantities | Matrices, small bars, side-by-side comparisons |

Let the subject determine the shape. A mixed view, a zoomed detail, or a novel arrangement may explain more than a familiar box diagram. Use a table when lookup or comparison is the point; use spatial relationships when adjacency, extent, or overlap matters. A simple sentence may need no diagram.

Browse [references/patterns.md](references/patterns.md) when a concrete example would spark an idea. Borrow a useful technique, not the entire layout. There is no required schema, renderer, script, or fixed output structure.

## Keep the Explanation Faithful

- Ground claims about an existing system in the supplied facts or relevant sources. Mark assumptions, unknowns, and illustrative examples. A possible trace is not a guarantee, and a workflow drawing is not evidence that it ran.
- Make consequential relationships clear: ownership versus reference, dependency versus execution order, a branch versus parallel work. Label arrows or joins when their meaning could be confused.
- Preserve identities across views. A repeated shared object is still one object; a zoom or snapshot should make its viewpoint clear.
- For quantitative drawings, state units, origins, endpoints, and scale as needed. If lengths are schematic, say so. Keep unknown, empty, zero, and omitted distinct.
- Include the exception or boundary that changes the conclusion. Avoid adding behavior just to make a diagram look complete or symmetric.

## Make It Easy to Read

Use fenced `text` blocks, spaces, and portable ASCII marks such as `+ - | / \ > <`. Aim for roughly 80 display columns, or the user's limit. Short labels and a nearby key can keep a dense drawing readable; English identifiers often align better than mixed-width labels.

Follow connectors to their endpoints. Check labels, junctions, carets, and related views for agreement with the explanation. Simplify a confusing drawing, split it, or change its form. Choose any task-appropriate tools when useful; this skill imposes no calculation or validation workflow.

Let the visual carry the relationships. Add the main point and only the assumptions, exceptions, or reading instructions it needs. Avoid narrating every label or repeating the same information in a second full view.
