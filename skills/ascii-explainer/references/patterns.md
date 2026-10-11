# ASCII Patterns

These original teaching examples are a sketchbook, not a template catalog. Borrow, combine, rotate, simplify, or replace their visual ideas to fit the question. Their shapes do not define the scope of this skill or describe a particular project.

Contents: [code architecture](#code-architecture), [control flow](#control-flow), [relationships](#relationships), [branches and retries](#branches-and-retries), [ordering and interleaving](#ordering-and-interleaving), [typed flow](#typed-flow), [snapshots and effective views](#snapshots-and-effective-views), [layouts and ranges](#layouts-and-ranges), [annotations and reasoning](#annotations-and-reasoning), [comparisons](#comparisons).

## Code Architecture

Choose nodes for the question: modules for dependencies, collaborating objects for a call path, or processes and external systems for deployment. Group by responsibility; expand one component when its internals matter. A folder tree is useful for navigation but does not establish calls, ownership, or runtime boundaries.

These two views of an invented checkout system answer different questions:

```text
Source dependencies:

[Checkout] -- imports --> [OrderStore] <-- implements -- [SqlOrderStore]
```

```text
One runtime path; --> means a call:

[Handler] --> [Checkout] --> [SqlOrderStore] --> [DB client]
                                                   |
                                                  SQL
                                                   v
                                             (External DB)
```

`OrderStore` is an interface; the example assumes application wiring supplies `SqlOrderStore`. It is not an extra runtime hop. In real code, inspect that wiring before naming the active implementation. A dependency arrow and a runtime call can point differently; keep their meanings explicit.

Other useful directions: draw ownership as containment, put shared state beside its readers and writers, or follow an event across a queue into a consumer. Label a process, thread, or network boundary only when established. A function call alone does not imply a boundary, and a queued message does not imply immediate execution or completion.

For a large system, keep a few recognizable components in the overview and use a separate detail for the reader's question. Keep names stable across views. Add a short caption about scope or omitted machinery rather than squeezing every class and edge into one picture.

## Control Flow

Find the trigger and follow the decisions that change the outcome. Use action labels for steps and conditions on branch exits. Straight paths, decision trees, loops, swimlanes, and state transitions are all options; a flowchart need not resemble every other flowchart.

This invented handler releases an acquired handle on either processing outcome. Assume failed acquisition leaves no handle and release itself cannot fail:

```text
[Request]
    |
 <valid?> -- no --> [Reject]
    | yes
 [Acquire] -- failed --> [Report failure]
    | acquired
 [Process]
    |
 <outcome>
    +-- success --> [Save result] --+
    `-- failure --> [Save error] ---+
                                   |
                            [Release handle]
                                   |
                         [Return saved outcome]
```

The merge shares cleanup, not the saved result: success and failure still return different outcomes. In real code, check returns, thrown errors, and cleanup scope before drawing a common exit. Do not invent a failure policy to complete a symmetric branch.

For a loop, make the return target and exit condition visible; use a labeled back-reference when a long connector obscures the path. Distinguish retry from normal iteration. For asynchronous work, consider separate caller/worker lanes so returning to the caller is not mistaken for completing the work. A branch selects a path; a fork starts concurrent work and needs its own join semantics.

A useful caption says what starts the flow and what its endpoints mean. A short note can explain a non-obvious condition or exception. Keep source links and long explanations outside the drawing so its path remains easy to scan.

## Relationships

Use a tree for hierarchy. Use labeled references when the structure shares an object:

```text
App
+-- Worker A -- uses --> [Q: shared queue]
`-- Worker B -- uses --> [Q]

[Q] always refers to the same queue.
```

The tree expresses membership; `uses` expresses a reference. Neither implies ownership of the queue. For entity relationships, state multiplicity in words or a legend rather than relying on unexplained endpoint symbols.

## Branches and Retries

Use a back-reference when a return connector would cross another branch:

```text
[A: attempt; consume one attempt] --> <outcome>
                                        |
     +----------------------------------+
     |
     +-- success ----------------------------> [Done]
     +-- retryable AND attempts remain ------> [A]
     `-- otherwise --------------------------> [Failed]
```

`[A]` returns to the same step. Assume a positive initial attempt budget. A retryable result with no attempts remaining follows `otherwise`. Do not add backoff, idempotency, or cancellation guarantees without evidence.

## Ordering and Interleaving

For constraints rather than a schedule:

```text
[A done] --+
           +--> [join: ALL] --> [C may start]
[B done] --+
```

A and B may finish in either order. Their overlap is unspecified. If the rule is ANY, show that rule and explain remaining work only if its disposition is known.

For a race, show a concrete possible trace. Assume `x = 0` and each increment is a separate read followed by a write:

```text
step   Worker A            Worker B            x
 1     read x -> a = 0                         0
 2                        read x -> b = 0      0
 3     write a + 1                             1
 4                        write b + 1          1
```

The trace shows one lost update, not that every run loses one. Rows are ordered events, not equal durations. For message lanes, label send/receive and blocking separately; do not infer a cross-thread order without a synchronization edge.

## Typed Flow

Name the data on either side of a transformation:

```text
packet --> [decode] --> frame --> [filter] --> frame --> [encode] --> packet
```

Here `packet` means encoded data and `frame` means raw media. This is a schematic for one media stream; packet/frame counts and timing are unspecified. When comparing a bypass, keep the same input/output viewpoint and state which transformations are skipped. A bypass does not mean that no other processing occurs.

Use separate diagrams for structure, establishment order, and teardown order if they differ. For network or security explanations, identify the endpoints of each connection or protection boundary; one encrypted hop does not establish end-to-end encryption.

## Snapshots and Effective Views

Keep identities and the viewing direction stable. This FIFO enqueues C, then dequeues A:

```text
step 0     front -> [A][B]    <- back
enqueue C  front -> [A][B][C] <- back
dequeue A  front -> [B][C]    <- back     returned: A
```

This shows logical order, not physical memory movement. Label a ring buffer's head/tail conventions explicitly rather than assuming those names identify the same ends in every implementation.

For overlays, show the effective result on the same axis. Here each character is one address unit, addresses use hexadecimal, and an override wins wherever it has coverage:

```text
address:   0123456789AB
base:      aaaaaaaaaaaa
override:  ....BBBB....
effective: aaaaBBBBaaaa

. = no coverage in this layer
```

The override covers `[4, 8)`. For nested regions, state which priorities are compared and whether a gap falls through, uses a parent's backing, or has no mapping. Do not generalize this simple overlay rule to another system without checking it.

## Layouts and Ranges

Separate exact bit positions from label width. This invented one-byte format has a 3-bit mode and a 5-bit count:

```text
bit:    7 6 5 | 4 3 2 1 0
field:  M M M | C C C C C

M = mode (3 bits); C = count (5 bits)
```

Check that widths sum to 8. For larger structures, include reserved/padding fields and variant layouts when relevant. Bit numbering here says nothing about the byte order of a multi-byte value.

For endpoint questions, an interval is often clearer than a box:

```text
valid byte offsets:  [0, 8)   = 0 through 7
requested offsets:   [6, 10)  = 6 through 9
outside valid range: [8, 10)  = 8 and 9
```

If drawing proportional ranges, preserve scale; otherwise label them schematic and provide exact bounds. Check nonzero origins and empty ranges, not only examples starting at zero.

## Annotations and Reasoning

Anchor an explanation to the exact disputed span. This invented API requires an integer:

```text
send(user_id)
     ^^^^^^^
     actual: string; expected: integer
```

For algorithm reasoning, align the candidate with the evidence:

```text
position: 012345
text:     ABABAC
pattern:  ABAC
             ^ mismatch: B != C
shift 1:   ABAC
           ^ mismatch: B != A
shift 2:    ABAC
            ^^^^ match
```

This checks three placements for this input. It does not prove that shifting by two is always safe. A general skip rule needs a precondition or invariant that excludes every skipped candidate. A counterexample can refute a claim; a successful example cannot establish all cases.

## Comparisons

Use a matrix when criteria matter more than connections. Keep criteria, units, and missing-data conventions identical; do not invent scores or trade-offs to complete a symmetric table.

For small quantities, use a stated scale and a common baseline:

```text
queued tasks; one # = two tasks
A  ####     8
B  ##       4
C  ?        unknown
```

`?` is unknown, not zero. Give exact values alongside rounded bars. Distinguish counts, rates, and durations; avoid proportional bars when the required values are unavailable.

## Why These Checks Matter

These historical examples explain the checks; they are not runtime dependencies:

- [CPython correction](https://github.com/python/cpython/commit/69d9a080993902b289c1b2c089cc0882b908df4c): moved match/mismatch markers to the correct columns.
- [QEMU review](https://lists.gnu.org/archive/html/qemu-devel/2013-09/msg02631.html) clarified recursive gaps and termination; a [later fix](https://github.com/qemu/qemu/commit/8210f5f6f52159b0d3a27ffe4af97056ac44cba8) corrected reversed priority values. Reviewed examples still need numerical checks.
- [OpenZFS correction](https://github.com/openzfs/zfs/commit/00ce064d8f9c2e1ab8154631add7d4006ea16f70): restored padding in an encrypted-block layout to match the field width.
- [GCC correction](https://github.com/gcc-mirror/gcc/commit/a7be993806a90a58397e9d5bc9b54160ac9f35db): excluded formatting codes from label display width.
- [FFmpeg rewrite](https://github.com/FFmpeg/FFmpeg/commit/794308c61b386b613f7e68b317dfa7debddf2f07): reorganized diagrams around actual components and typed data flow. A separate [implementation fix](https://github.com/FFmpeg/FFmpeg/commit/338a5fcdbe9571e6f22817a111621259d83f2e59) records how relying on an incomplete specification figure produced incorrect behavior.
- [curl documentation update](https://github.com/curl/curl/commit/02d81c5a6808e189cd20418274abccbd9bb1385d): expanded filter flags and connection snapshots. This is an explanatory extension, not evidence of a reviewer finding a diagram error.
