# Smells

Detection vocabulary. Mostly Fowler, *Refactoring* (2nd ed.) ch.3, with Martin's *Clean Code* ch.17 and Kerievsky's smell→pattern mapping.

A smell is a hint, never a verdict. Every entry here has cases where leaving it alone is correct. The value of naming one is that it comes with a known remedy — "this feels messy" is not actionable; "Feature Envy, move the method to `Invoice`" is.

## Bloaters

| Smell | The tell | Usual remedy |
| --- | --- | --- |
| Long Function | You cannot see it at once; needs comments to navigate | Extract Function — but only where the extraction *hides* something (see complexity.md). Extract Function + Replace Temp with Query |
| Large Class | Too many fields; subsets of fields used by disjoint method groups | Extract Class along the field clusters, Extract Superclass |
| Long Parameter List | 4+ params, or params only passed onward | Introduce Parameter Object, Preserve Whole Object, Replace Parameter with Query |
| Data Clumps | The same 3 fields travel together through many signatures | Extract Class, Introduce Parameter Object |
| Primitive Obsession | Money as `float`, IDs as `str`, currency as a magic string, ranges as two ints | Replace Primitive with Object, Replace Type Code with Subclasses |

## Change-resistance

| Smell | The tell | Usual remedy |
| --- | --- | --- |
| Divergent Change | One module changed for several unrelated reasons | Split Phase, Extract Class — one reason to change per module |
| Shotgun Surgery | One conceptual change requires many small edits across files | Move Function/Field to consolidate, Combine Functions into Class |
| Parallel Inheritance | Every new subclass here forces one there | Move the varying behavior into one hierarchy; Replace Inheritance with Delegation |

Shotgun Surgery in a diff is a strong signal: if the change itself had to touch seven files to add one field, the *next* one will too. That's a present-tense cost, so it clears the gate.

## Couplers

| Smell | The tell | Usual remedy |
| --- | --- | --- |
| Feature Envy | A function reaches into another object's data more than its own | Move Function, Extract Function then move |
| Inappropriate Intimacy | Two classes touch each other's internals | Move Function/Field, Replace Bidirectional with Unidirectional, Extract Class |
| Message Chains | `a.b().c().d()` | Hide Delegate, or Extract the underlying question as a method |
| Middle Man | A class that delegates nearly everything | Remove Middle Man, Inline Function |
| Insider Trading | Modules trading data through back channels | Move Function, Introduce an explicit intermediary — but only one |

## Dispensables

| Smell | The tell | Usual remedy |
| --- | --- | --- |
| Duplicated Code | Change one, must change the other | Extract Function, Pull Up Method, Form Template Method — after the rule of three |
| Speculative Generality | Abstraction with one user; hooks nothing calls; a param always the same value | Collapse Hierarchy, Inline, Remove Dead Parameter. **The most common thing to flag in an over-designed diff.** |
| Dead Code | Unreachable, or reachable only from tests | Delete it. Version control remembers |
| Lazy Element | A class or function that adds a name and nothing else | Inline |
| Comments as deodorant | A comment explaining a confusing block | Extract Function with a name that says it, or fix the name |
| Data Class | Fields and accessors, behavior lives in callers | Move Function into it — or accept it as a DTO at a boundary, which is legitimate |

## Others worth watching in backend diffs

| Smell | The tell | Usual remedy |
| --- | --- | --- |
| Repeated Switch | The same `if`/`match` over a type code in several places | Replace Conditional with Polymorphism, or a dispatch table |
| Mutable Data / shared state | A structure mutated across call boundaries; a default arg that is a list or dict | Encapsulate Variable, Split Variable, Replace Derived with Query, Combine Functions into Transform |
| Temporary Field | A field set only during one operation | Extract Class for that operation, Introduce Special Case |
| Flag Argument | `do_thing(x, force=True)` — the call site does not read | Replace Parameter with Explicit Methods |
| Nested Conditional | 3+ levels of nesting | Replace Nested Conditional with Guard Clauses, Decompose Conditional |
| Refused Bequest | A subclass ignoring most of what it inherits | Replace Inheritance with Delegation, Push Down Method |
| Loops that do three things | Filtering, transforming, and accumulating in one body | Split Loop, then Replace Loop with Pipeline |
| Exceptions as control flow | `try/except` around expected outcomes | Replace Exception with Precondition Check; or define the error out of existence |
| Leaky boundary | ORM models, HTTP shapes, or DB rows escaping their layer | Introduce a boundary type at the edge only — one, not one per layer |

## Smells in tests

Worth reviewing, and usually left unreviewed:

- **Mystery Guest** — a test depending on unseen fixture state.
- **Assertion Roulette** — many bare assertions, so a failure does not say what broke.
- **Over-mocking** — mocks asserting on implementation calls rather than outcomes; the test now fails on every refactoring, which makes the code *harder* to change.
- **Test duplication that hides the interesting variable** — table-driven cases where the thing that varies is buried in setup.

A change that adds behavior with no test for its failure mode is a Blocking-severity gap in a way that untidy code usually is not.
