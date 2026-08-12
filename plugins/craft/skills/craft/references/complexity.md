# Complexity

The primary lens. Mostly Ousterhout, *A Philosophy of Software Design*, with Parnas on module boundaries.

Complexity is anything that makes a system hard to understand or modify. It shows up as three symptoms:

- **Change amplification** — a simple-seeming change requires edits in many places.
- **Cognitive load** — how much you must know to make a change safely.
- **Unknown unknowns** — you cannot tell *which* code you need to read to change something safely. The worst of the three, because there is no signal that you are about to break something.

Complexity accumulates in increments, so no single change looks like the problem. That is exactly why it gets reviewed at the diff level.

## Deep vs shallow

A module's value is `benefit − cost`, where benefit is the functionality hidden and cost is the interface a caller must learn.

- **Deep**: small interface, substantial hidden work. `open(path)` hides the filesystem.
- **Shallow**: interface nearly as large as the implementation. A wrapper that forwards five arguments and returns the result unchanged has negative value — the caller now learns two things instead of one.

This is where Clean Code's "extract until you drop" advice cuts against you. Extraction that produces shallow units *adds* complexity: more names to learn, more jumping between definitions, and the original logic now spread across places where you can no longer see it at once. Extract when it hides something. Do not extract to hit a line count.

**In review:** for each new function, class, or module in the diff, ask what a caller no longer needs to know. If the answer is "nothing", it is a shallow unit and its existence is the finding.

## Information leakage

Two or more places encode the same design decision, so both must change together — and nothing in the code says so. The strongest signal that two units should be one, or that a piece of knowledge belongs in exactly one of them.

Common in diffs as: a parser and a writer that both know the field order; a caller that reconstructs state the callee already computed; validation duplicated at the boundary and in the core; a magic string shared across layers.

Distinct from duplication — the *code* may look nothing alike. What is shared is knowledge.

## Temporal decomposition

Splitting modules by *when* things happen rather than by *what knowledge they hold*. `read_config` / `validate_config` / `apply_config` as three modules each knowing the config schema means every schema change touches all three.

Execution order is a poor basis for a boundary because it changes for reasons unrelated to knowledge. Group by what must know the same thing.

## Pass-through methods and parameters

A method that does nothing but call another with the same signature. A parameter threaded through five layers because only the bottom one uses it. Both are signals that a boundary is in the wrong place — the layers are not adding abstraction, only distance.

Threading a value through many layers is sometimes still the least-bad option; the alternatives (a context object, a global, a mutable session) have their own costs. Flag it when the chain is long and the value is unrelated to the intermediate layers' jobs.

## Pushing complexity down, not up

Where a hard problem must live, it should live in the module rather than in every caller. A configuration parameter is often complexity pushed *up*: the module author, who understands the tradeoff, has handed the decision to callers who do not. Ask whether the module could compute or default a good value instead.

Corollary: it is right for a module to be *more* complex internally if that makes its interface simpler. One hard function beats twenty callers each getting it slightly wrong.

## Define errors out of existence

The best exception is one that cannot happen. Prefer designs where the error case is not reachable: an operation that is idempotent rather than one that must check first; `delete` that succeeds on a missing key; a range that clamps rather than raising.

Second best: handle it at one place high enough up to know what to do. Worst, and common in diffs: caught, logged, and swallowed at every layer, so the happy path is unreadable and failures are invisible.

## Comments as a design tool

If a function is hard to comment without describing its implementation, the abstraction is probably leaky. A comment that has to explain *how* rather than *what* and *why* is a design signal, not a documentation failure. Comments should say what the code cannot: why this way, what the invariant is, what the units are, what callers must not do.

Comments that restate the code, or that contradict it, are noise — but "delete the comment" is rarely the fix. Ask whether the name should have carried the meaning instead.

## Strategic vs tactical

Tactical programming optimizes for finishing this change. Strategic accepts a slightly larger change now for a design that stays workable. The review's job is to find the small strategic investment worth making *in this diff* — not to relitigate the architecture. If the right fix is a rewrite, say so once, briefly, and move on to what is actionable.
