# Deterministic checks

Use Python 3.10+ and the bundled `scripts/check.py`. It uses only the standard library, reads local JSON, and has no network or write operations. Create temporary inputs outside the skill folder. All numbers are integers or strings such as `"0x20"` or `"-3"`; booleans and floating-point values are rejected. IDs use 1–20 ASCII letters, digits, `.`, `_`, or `-`, starting with a letter. `NONE` and `OUTSIDE` are reserved.

```sh
python3 /path/to/ascii-explainer/scripts/check.py /tmp/model.json
python3 /path/to/ascii-explainer/scripts/check.py /tmp/model.json --answer /tmp/answer.md
```

The first command returns `ok`, computed `facts`, and ready-to-copy `tables`. Exit 2 means invalid input or a failed check; read the error and correct the model or proposed result against the source. Do not weaken the source constraints to get a pass. A document can contain one model or `{"models": [model1, model2]}` with distinct `id` values for scenario variants.

Write the answer with **each returned table as an unchanged fenced `text` block**, exactly once. The second command compares every fenced block with the returned tables, including spaces; it rejects missing, changed, extra, or duplicated blocks. Keep prose outside those blocks. This binds rendering to the checked model. It does not check natural-language claims or whether the input faithfully represents the user's facts. Review those separately, including units, coordinate origins, dependencies, omitted cases, and unknown behavior. The checker never establishes that a real implementation ran successfully.

## Ranges

Supported semantics: half-open integer intervals, larger priority first among siblings, pure containers that fall through when no child matches, optional shared backing offsets. **Every region's `start` and `end` are relative to its parent's start, including root children.** The root's own `start` and `end` are absolute. Children must fit inside their parent; equal-priority overlapping siblings are rejected because no tie rule is supplied. Other priority, clipping, or parent-backing semantics are not modeled.

```json
{
  "kind": "ranges", "id": "coverage", "base": 16,
  "start": "0x80", "end": "0x88",
  "regions": [
    {"id": "base", "start": 0, "end": 8, "priority": 0},
    {"id": "layer", "start": 2, "end": 6, "priority": 4,
     "children": [{"id": "block", "start": 1, "end": 2,
                   "priority": -1, "result": "DENY"}]}
  ],
  "queries": ["0x83", "0x84", "0x88"]
}
```

A node with `children` is a pure container, including `children: []`. A leaf returns its `id`, or its explicit `result`; `DENY` and `BLOCK` are ordinary terminal results, not gaps. No match returns `NONE`; a query outside the root returns `OUTSIDE`.

For actual memory, declare `backings: {"mem": 8}` on the model. A leaf may use `"backing": "mem", "offset": 0`; the checker validates bounds and computes the backing offset for each effective segment and query. Two leaf mappings can reference the same backing. No backing is invented for non-memory hit tests.

Optional `claims` are absolute, nonempty segments that must partition the whole root: `[{"start": 128, "end": 131, "region": "base"}, ...]`. Use `region: null` for a gap. Incorrect targets, gaps, or overlaps are rejected; different valid splitting is allowed. Output `normalized_regions` lets you check offset transcription.

## Fields

Byte offsets are absolute; fields are sequential. Each field has `id` and exactly one of:

- `size`: a nonnegative byte count, or `{"count": "earlier_field", "unit_bits": 1}`. The latter computes `ceil(count * unit_bits / 8)`; use `unit_bits: 8` for byte counts.
- `align`: a positive integer. This inserts padding until the **absolute** next offset is divisible by `align`, possibly zero bytes.

```json
{
  "kind": "fields", "id": "record", "origin": 1, "base": 16,
  "data": "02 31 32 00 FF",
  "fields": [
    {"id": "count", "size": 1, "endian": "big"},
    {"id": "payload", "size": {"count": "count", "unit_bits": 8}},
    {"id": "pad", "align": 5, "zero": true},
    {"id": "CRC", "size": 1}
  ],
  "checksums": [{"field": "CRC", "covers": ["count", "payload"]}]
}
```

`data` is an optional received byte prefix in hexadecimal. Excess bytes are rejected; facts include received and missing byte counts. To calculate a hypothetical variant without bytes, provide `value` on its integer fields instead. With both data and value, they must agree, including any supplied prefix. An integer field requires `endian: "little"` or `"big"` and size 1–8 bytes. Without data or value its value is unknown; a later count cannot use an unknown value.

A decoded integer can have `bits: [{"id": "flag", "lsb": 7, "width": 1}, ...]`. These entries must cover the integer exactly without overlap; include reserved bits. Optional `equals: 0` checks required zero bits. Returned binary values include leading zeros to the declared width. Bit numbering does not determine byte endianness.

A payload can have `tail_bits_from: "bit_count"`: its size must be `ceil(bit_count/8)`, and unused high bits in the last received complete payload are checked for zero. Declare `zero: true` for required-zero padding/reserved bytes even without received data; it checks supplied bytes and displays `zero required` for unreceived bytes. An empty field remains a zero-size row, not an occupied cell. Decoded integers are marked `(dec)`; byte sequences are marked `(hex)`, with `??` for missing bytes. `?` means no value or byte prefix was supplied.

`checksums` computes coverage and byte counts for named fields; it **does not** verify a checksum algorithm or decompression. Optional `claims: [{"id": "payload", "start": 2, "end": 4, "size": 2}]` rejects wrong field bounds or sizes.

## Schedules

Supported semantics: positive integer durations, nonpreemptive tasks, finish-to-start dependencies, interchangeable units within each named resource group, and full-duration exclusive resource use. Time starts at zero. Releases, deadlines, setup costs, partial resource holding, and preemption are not modeled.

```json
{
  "kind": "schedule", "id": "plan",
  "resources": {"worker": ["W1", "W2"], "device": ["G1"]},
  "tasks": [
    {"id": "A", "duration": 2, "after": [], "needs": {"worker": 1, "device": 1}},
    {"id": "B", "duration": 1, "after": ["A"], "needs": {"worker": 1}}
  ],
  "plan": [
    {"id": "A", "start": 0, "end": 2, "using": ["W1", "G1"]},
    {"id": "B", "start": 2, "end": 3, "using": ["W2"]}
  ]
}
```

The checker requires every task exactly once. It checks durations, dependencies, assigned resource types/counts, and conflicts on each resource unit. It computes elapsed time and busy resource-time per group. Keep each changed scenario in its own model; update the supplied durations/resources and plan together.

A valid schedule is not automatically optimal. The checker computes a lower bound from the critical path and pooled resource loads. It returns `proven_by_bound` only if the supplied feasible plan reaches that bound. Otherwise it returns `not_proven`, even if the plan happens to be optimal. Supply a separate sound proof when needed; do not describe a feasibility pass as an optimality proof.

## Limits

A successful check validates the structured model and, with `--answer`, exact table reuse. It does not validate source transcription, prose, unsupported semantics, or arbitrary hand-drawn ASCII. If the model does not fit, say which claim remains unchecked; do not silently change the problem to fit the checker. Run the bundled rejection tests with `python3 scripts/test_check.py` when changing the checker.
