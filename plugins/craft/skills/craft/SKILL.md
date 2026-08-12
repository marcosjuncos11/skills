---
name: craft
description: Review a code change for design quality — code smells, needless complexity, readability, and whether a design pattern would genuinely simplify it. Use when the user asks to review, critique, clean up, simplify, refactor, or improve the design of a diff, PR, branch, or recent edits, or asks things like "can this be simpler", "does this smell", "is this well designed", "am I over-engineering this". Not a correctness or security review — that is what /code-review is for.
argument-hint: "[staged | branch | <base-ref> | <path> | pr <n>] (empty = working tree)"
effort: high
allowed-tools: Bash(git *) Bash(gh pr diff *) Bash(gh pr view *)
---

# Craft review

Judge a change on how it will read and change six months from now. Not on whether it works.

## Orientation

Branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || true`
Working tree: !`git status --short 2>/dev/null || true`
Shape of uncommitted work: !`git diff --stat HEAD 2>/dev/null || true`

## Step 1 — Resolve the scope

Pick the diff from `$ARGUMENTS`:

| Argument | Command |
| --- | --- |
| (empty) | `git diff HEAD` — if empty, fall back to the branch diff below |
| `staged` | `git diff --cached` |
| `branch` | `git diff $(git merge-base HEAD origin/main \|\| git merge-base HEAD main)...HEAD` |
| a ref | `git diff <ref>...HEAD` |
| a path | `git diff HEAD -- <path>` |
| `pr <n>` | `gh pr diff <n>` |

If the resolved diff is empty, say so and stop. Do not review from memory or from open files.

## Step 2 — Read the surroundings, then form the intent

Read each changed file in full, plus its immediate collaborators (callers, the module it exports into, sibling implementations of the same interface). A hunk cannot be judged on its own: whether a new abstraction is warranted depends entirely on what already exists next to it.

Then state, in one sentence to yourself, what this change is *for*. Every finding below is measured against that intent. A review that misunderstands the intent produces confidently wrong advice, which is worse than no review.

If the intent is genuinely unclear from the code, ask before reviewing.

## Step 3 — Six passes, in this order

Order matters: complexity findings subsume smell findings, and smell findings are what justify patterns. Working backwards produces pattern-shaped solutions to problems that don't exist.

**1. Complexity** — the arbiter. For each new or modified unit: is it *deep* (small interface, meaningful work hidden) or *shallow* (interface nearly as large as the implementation)? Look for information leakage (two places that must both change together), pass-through methods, temporal decomposition (split by execution order rather than by knowledge), and configuration parameters that push a decision onto the caller who knows less than you do. See `references/complexity.md`.

**2. Smells** — the vocabulary. Name what is wrong using the standard catalog rather than "this feels off". A named smell comes with a known refactoring, which makes the advice actionable. See `references/smells.md`.

**3. Duplication** — DRY, applied in both directions. Real duplication (change one, must change the other) is a cost worth removing. Incidental similarity is not — collapsing it produces an abstraction that will be wrong the first time the two cases diverge. Rule of three. Prefer duplication over the wrong abstraction. YAGNI is the tiebreaker: if the justification for the shared abstraction is a future case, the answer is no.

**4. Readability** — nesting depth and cyclomatic complexity: 3+ levels of nesting or a function whose branch count you cannot hold in your head gets guard clauses, early returns, or Decompose Conditional before anything fancier. Also: names that state the concept rather than the type, boolean parameters at call sites, negated conditionals, magic values, error handling that buries the happy path, comments that restate the code or contradict it. Long functions and large classes belong to pass 2's vocabulary (Long Function, Large Class) — break them along responsibility seams, not line counts.

**5. Patterns & principles** — only for pains already found in passes 1-4. Map the smell to the pattern, never the reverse. SOLID applies here with the caveats in the reference (Single Responsibility as "one reason to change", Liskov violations as live bugs, Dependency Inversion only where something concrete breaks). If no earlier pass found a pain, this pass produces nothing, and that is a normal outcome. See `references/patterns.md`.

**6. Seams** — can the change be tested without standing up the world? Hidden dependencies, hard-coded collaborators, clock/randomness/network/IO reached for directly instead of passed in.

## Step 4 — Gate every proposal

A finding only survives if all five hold. Drop it otherwise; do not soften it into a "consider maybe".

1. It names a specific smell or complexity cost at a specific location.
2. The cost is **present tense and concrete** — someone reading or changing this code will pay it. Not "if we ever add another provider".
3. The proposed code is smaller or flatter than what it replaces, *or* it removes a real risk (a footgun, a silent failure, a lock held too long).
4. It does not add an indirection whose only justification is future flexibility.
5. The author can do it now, in this change, without a rewrite.

Then apply the counterweight — these are things to argue *against*, not for:

- An interface with one implementation and no second one in sight.
- Splitting a coherent function into single-use fragments whose names restate their bodies. Length is not the metric; coupling and depth are.
- A pattern that adds a class to remove an `if`.
- Config for a value that has never changed.
- A layer added so the code "matches the architecture" when nothing else needs it.
- Renaming or reformatting for taste. Not a finding.

If the change is already good, say that plainly and stop. Manufacturing findings to look thorough trains the author to ignore you.

## Step 5 — Output

Do not edit files. Propose; let the author choose. If they ask for the edits afterwards, apply only the ones they picked.

```
**Verdict:** <one line — is this good to merge as-is, worth one pass, or does it need rework>

**<Blocking | Worth doing | Taste>** — <file>:<line> — <smell name>
<One or two sentences: what the cost is, in present tense.>
<Proposed code, as a minimal diff or snippet.>
<Cost of the fix, if it is not obviously cheap.>

... (repeat, ordered by leverage, at most 5 — if there are more, say so and cover the top 5)

**Considered and rejected**
- <thing a reviewer might have flagged> — <why leaving it alone is right here>

**Reading**
<At most two pointers, only where the idea is worth more than the fix: e.g. "Ousterhout ch.4 on deep modules", "Fowler, Replace Conditional with Polymorphism". Skip entirely if nothing warrants it.>
```

Severity means: **Blocking** — will cause bugs or make the next change dangerous. Cleanliness alone is never blocking. **Worth doing** — pays for itself within this change. **Taste** — defensible either way, author's call.

Anchor each finding to a real line from the diff. If you cannot point at the line, you do not have the finding.
