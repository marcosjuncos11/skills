# Patterns

Read this only after a pass found a concrete pain. Patterns are named solutions to *recurring* problems; a pattern applied to a problem you do not have is pure cost — a class, a name, an indirection, and a reader who now has to learn the pattern to follow the code.

The honest framing (Kerievsky, *Refactoring to Patterns*): you refactor *toward* a pattern when the code has told you it needs one, and sometimes *away* from one when the flexibility never got used. Gamma, twenty years after GoF, said if he rewrote it he'd cut several patterns and reframe the rest around composition. Treat the catalog as a diagnosis-to-remedy index, not a checklist.

## Smell → pattern

Only these directions are legitimate. Never start from a pattern and look for somewhere to put it.

| The pain you actually found | Pattern worth proposing | Cheaper alternative to weigh first |
| --- | --- | --- |
| Same conditional over a type code in 3+ places | Strategy, or Replace Conditional with Polymorphism | A dict dispatch table, or one `match` in one place |
| Constructor doing conditional setup by type | Factory Method | A module-level function with a `match`; a classmethod |
| Object built across many steps, invalid in between | Builder | Keyword args with defaults; a frozen dataclass |
| An algorithm whose steps are fixed but details vary | Template Method | A function taking one callable |
| Adding behavior to something you cannot modify | Adapter, Decorator | A plain wrapper function |
| A subsystem exposing more than callers need | Facade | Just narrow the module's public surface |
| Traversing a structure with type-specific behavior scattered | Visitor | A `match` on the node type in one place — usually better in Python |
| A tree where leaves and branches are handled differently everywhere | Composite | A recursive function |
| Callers polling for change | Observer | A direct call; an event you already have |
| Repeated expensive construction of interchangeable objects | Flyweight, Object Pool | A `functools.cache` |
| `None` checks scattered for the same absent case | Special Case / Null Object | A default at the boundary where it enters |
| Two abstractions varying independently, multiplying subclasses | Bridge | Composition without the ceremony |
| One operation must span several stores or writes atomically | Unit of Work | An explicit transaction boundary at the entry point |
| Query logic duplicated across call sites | Repository, Query Object | A named function on the module |
| A domain rule reimplemented at several call sites | Specification, or just a named predicate | A named predicate. Usually stop here |

Note the third column. In Python especially, first-class functions, `dict`, `match`, `dataclass`, `functools`, `contextlib`, and protocols dissolve maybe half the GoF catalog. Proposing `Strategy` where a dict of functions does the job is the classic over-application, and it reads as a pattern-shaped ritual rather than a design.

## The three questions before proposing any pattern

1. **What is duplicated or fragile right now?** Point at lines. If you cannot, there is no pattern to propose.
2. **Is there a third case, or a concrete near-term second one?** Two cases justify a conditional. Three justify an abstraction over them. One justifies nothing.
3. **Does the pattern make the *call site* simpler?** If the callers get more complicated so an internal hierarchy can be elegant, the pattern lost.

## Patterns to argue against by default

- **Strategy / Factory with one strategy.** Speculative Generality wearing a respectable name.
- **Singleton.** A global with extra steps. Hidden dependency, untestable, order-dependent init. If something must be shared, pass it in.
- **A `BaseThing` with one subclass**, or an ABC with one implementation, added "for the interface". Extract the interface when the second implementation arrives; that is when you learn what it should be.
- **Layers mirroring each other.** A DTO per layer, mapped field-by-field, that adds no invariant. That is Shotgun Surgery, formalized.
- **Observer / event bus for a call between two things that know each other.** Traded a readable call graph for an unreadable one.
- **A pattern introduced alongside a feature.** Land the feature; refactor when the third case shows up. Two commits, both reviewable.

## Structural principles, with their honest caveats

- **Single Responsibility.** Useful phrasing: one reason to change. "Does one thing" is unfalsifiable at any granularity.
- **Open/Closed.** Real, but you cannot predict the axis of variation up front. Applied speculatively it produces exactly the extension points nobody uses. Let the second change tell you the axis.
- **Liskov.** Worth flagging when violated — a subclass narrowing preconditions or raising where the parent returns is a live bug source.
- **Interface Segregation.** In Python, usually about not requiring a fat object where a callable or a small protocol would do.
- **Dependency Inversion.** The most over-applied of the five. Inverting a dependency to make something testable is legitimate. Inverting it because a diagram says arrows point inward is ceremony. Ask what breaks if the concrete type stays.
- **Law of Demeter.** Good as a coupling smell detector (Message Chains), bad as a rule — mechanical compliance produces Middle Man wrappers, which is a worse smell than the chain.
- **Composition over inheritance.** Holds up better than almost anything else on this list.
- **Tell, don't ask.** Behavior near data. The main defense against anemic models and Feature Envy.
- **DRY.** About knowledge, not text: two code blocks that look alike but encode different decisions are not duplication, and deduplicating them couples things that should drift apart. The test is "if one changes, must the other?" — yes means extract, no means leave it. Rule of three before abstracting.
- **YAGNI.** The tiebreaker whenever a proposal's justification is a future case. If the argument is "we'll probably need it", the answer is no, and the cost of adding it later is almost always lower than the cost of carrying it wrong.

## Architecture-level, when the diff crosses layers

Only relevant if the change touches boundaries; do not raise it otherwise.

- Dependencies should point one way. A domain module importing from the transport or persistence layer is a real finding.
- Business rules should be reachable in a test without a database, a queue, or a clock.
- One translation at the edge. Every additional mapping layer needs to justify itself with an invariant it enforces.
- Transaction boundaries belong at a deliberate, visible place — not implicit in whichever function happens to touch the session.
- New I/O inside a loop, or a query inside an iteration, is a design finding even when it is fast today.
