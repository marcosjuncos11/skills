# The Zen of Python (PEP 20) as a review lens

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

The Zen doesn't add an extra pass. Each line sharpens a pass that already exists, and a Zen violation is a finding only when it also clears the gate in Step 4. When it does, put the line in the finding's header so the author gets the principle along with the fix.

It applies to any language. Quote it word for word on Python diffs, and use the idea without the quotation elsewhere.

| Aphorism | Pass | What to look for in a diff | Usual remedy |
| --- | --- | --- | --- |
| Beautiful is better than ugly. | 4 | Code whose shape hides its intent: tangled control flow, mixed levels of abstraction in one function | Usually covered by a more specific line below; cite this one only when none fits |
| Explicit is better than implicit. | 1, 4, 6 | Hidden behavior: mutable default args, `**kwargs` passthrough that hides the real contract, side effects in properties or `__init__`, magic via `getattr`/monkeypatching, implicit globals, a bare `datetime.now()` inside logic | Name the parameter, return the value, pass the dependency in |
| Simple is better than complex. | 1 | More machinery than the problem needs: a class where a function works, a framework hook where an `if` works | Delete the layer |
| Complex is better than complicated. | 1 | The inverse: logic smeared across many small pieces that must be read together to understand one behavior (shallow modules, pass-throughs) | Collapse into one deep unit with a small interface |
| Flat is better than nested. | 4 | 3+ levels of nesting, `if` inside `for` inside `try`, deep package or class hierarchies | Guard clauses, early returns, `continue`, Decompose Conditional |
| Sparse is better than dense. | 4 | Clever one-liners: nested comprehensions, chained ternaries, walrus-heavy expressions, long boolean chains | Split into named intermediate values |
| Readability counts. | 4 | Names that state type not concept, magic values, comments that restate code | Rename, name the constant, delete the comment |
| Special cases aren't special enough to break the rules. | 2, 3 | An `if customer_id == ...` branch, a one-off code path that bypasses the normal flow or validation | Fold the case into the general rule, or make it data |
| Although practicality beats purity. | Gate | A "cleaner" proposal that costs more than it saves | The counterweight list: drop the finding |
| Errors should never pass silently. | 4, 6 | Bare `except:`, `except Exception: pass`, swallowed errors that only log, returning `None` on failure where the caller can't tell, `.get()` defaults hiding missing data that should be required | Let it raise, raise a specific error, or handle it visibly. **Always at least Worth doing; Blocking when it can hide data loss** |
| Unless explicitly silenced. | 4 | Legitimate suppression without a reason | Narrow `except SpecificError`, `contextlib.suppress(...)`, plus a comment explaining why |
| In the face of ambiguity, refuse the temptation to guess. | 1, 4 | Code that guesses: silent type coercion, fuzzy fallbacks (`x or default` when `0`/`""` are valid), parsing that "tries" formats, picking the first match of several | Validate and fail loudly, or make the caller decide. Also applies to the review itself: if intent is unclear, ask (Step 2) |
| There should be one-- and preferably only one --obvious way to do it. | 3 | Two helpers that do the same thing, a new util next to an existing one, a second config path, mixed styles for the same operation in one module | Reuse the existing way; delete the duplicate |
| Although that way may not be obvious at first unless you're Dutch. | — | No review use. Don't cite it. | — |
| Now is better than never. | Gate | Over-cautious TODOs deferring a cheap fix that belongs in this change | Do it now if it clears gate clause 5 |
| Although never is often better than *right* now. | Gate, 3 | Speculative generality: hooks, params, abstractions for a future case | YAGNI: remove it |
| If the implementation is hard to explain, it's a bad idea. | 1 | You can't summarize what a unit does in one sentence without "and" or "depending on" | Split along the responsibility seam, or simplify |
| If the implementation is easy to explain, it may be a good idea. | Rejected | Code that reads plainly but a pattern-minded reviewer might want to restructure | List it under **Considered and rejected** |
| Namespaces are one honking great idea -- let's do more of those! | 2, 6 | `from x import *`, name collisions, module-level globals as shared state, a dumping-ground `utils.py`, prefixes standing in for a module (`vault_checklist_build`, `vault_checklist_send`) | Proper modules or classes; import the module, not the names |
