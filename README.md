# skills

Claude Code skills I actually use. Each one lives in `plugins/`, and the repo doubles as a plugin marketplace so you can install from it directly and get updates.

| Skill | Command | What it does |
| --- | --- | --- |
| [craft](plugins/craft) | `/craft` | Reviews a diff for design quality — code smells, needless complexity, readability, and whether a design pattern would genuinely simplify it |

---

## Install

Three ways, depending on how you want to live with it.

### 1. As a plugin (recommended)

Gets you versioning and one-command updates.

```bash
# in Claude Code
/plugin marketplace add marcosjuncos11/skills
/plugin install craft@marcosjuncos-skills
```

If the install summary says `Run /reload-plugins to activate`, do that. Then `/craft` works. The namespaced form `/craft:craft` also works and is what you'd use if the bare name ever collides with something else.

Update later with:

```bash
/plugin marketplace update marcosjuncos-skills
```

### 2. As a personal skill (all your projects, no plugin layer)

Symlink so a `git pull` is the whole update process:

```bash
git clone https://github.com/marcosjuncos11/skills.git ~/src/claude-skills
ln -s ~/src/claude-skills/plugins/craft/skills/craft ~/.claude/skills/craft
```

Claude Code follows the symlink and watches the directory, so edits to `SKILL.md` take effect in the current session without a restart.

### 3. As a project skill (committed, shared with the team)

```bash
cp -r plugins/craft/skills/craft <your-repo>/.claude/skills/craft
```

Commit it. Everyone who clones gets `/craft`. Note that project skills with `allowed-tools` only take effect after each person accepts the workspace trust dialog — which is the correct behavior, since a skill in a repo can grant itself tool access.

**Precedence,** if you end up with more than one copy: enterprise > personal > project, and any of those overrides a bundled skill of the same name. Plugin skills are namespaced (`craft:craft`) so they never collide.

---

## Using `/craft`

```bash
/craft                  # uncommitted work (git diff HEAD)
/craft staged           # git diff --cached — good as a pre-commit gate
/craft branch           # everything since the merge-base with main
/craft origin/develop   # against an arbitrary ref
/craft app/vault/       # scope to a path
/craft pr 412           # pulls the diff via gh
```

It also fires without the slash when you ask for it in words — "is this over-engineered?", "can this be simpler?", "review the design of what you just wrote" — because the skill is model-invocable. That last case is the one worth knowing about: it works on changes Claude made earlier in the same session.

It does not edit files. It proposes, you pick, and then you tell it which ones to apply.

---

## What it's for, and what it isn't

`/craft` reviews **design**: how the code will read and change six months from now.

It is not a correctness or security review. Claude Code ships `/code-review` for that, and the two compose — run `/code-review` for bugs, `/craft` for shape. Overlapping them just produces two reviews that each half-cover both jobs.

It is also not a linter. Formatting, import order, and naming-for-taste are explicitly out of scope; your existing tooling is better at those and cheaper to run.

---

## How it's built

```
plugins/craft/skills/craft/
├── SKILL.md                    # the procedure — ~100 lines, stays in context
└── references/
    ├── complexity.md           # loaded during pass 1
    ├── smells.md               # loaded during pass 2
    └── patterns.md             # loaded during pass 5
```

Once a skill is invoked, its rendered body stays in context for the rest of the session. That makes every line of `SKILL.md` a recurring token cost, so `SKILL.md` holds only the procedure and the reference material loads on demand — a design that costs nothing until a pass actually needs it.

### Six passes, in a deliberate order

Complexity → smells → duplication → readability → **patterns** → seams.

Patterns are fifth on purpose. A reviewer told to "apply design patterns" will find pattern opportunities everywhere and hand you an `AbstractStrategyFactoryProvider` for a thirty-line function. So the pattern pass is gated: it may only propose a pattern for a pain an *earlier* pass already located at a specific line. If passes 1–4 found nothing, pass 5 produces nothing, and the skill treats that as a normal outcome rather than a failure to be thorough.

`references/patterns.md` is deliberately hostile to its own subject. Every entry carries a "cheaper alternative to weigh first" column — because in Python, first-class functions, `dict`, `match`, `dataclass`, and `functools` dissolve maybe half the GoF catalog, and proposing `Strategy` where a dict of functions does the job reads as ritual rather than design.

### The books disagree, and the skill takes a side

*Clean Code* says functions should be around four lines. Ousterhout argues in *A Philosophy of Software Design* that this is precisely how you get shallow modules and pass-through methods — that extraction which doesn't *hide* anything adds complexity rather than removing it, because now there are more names to learn and the logic no longer fits in one view.

Pretending the canon is unanimous produces mush, so the skill picks: **Ousterhout's complexity test is the arbiter, Fowler's catalog is the detection vocabulary.** Smell names are for making advice actionable — "Feature Envy, move the method to `Invoice`" beats "this feels messy" — but whether a finding survives is decided by whether it reduces cognitive load, change amplification, or unknown-unknowns.

Drawn from: Fowler, *Refactoring* (2nd ed.) · Ousterhout, *A Philosophy of Software Design* · Martin, *Clean Code* · Gamma et al., *Design Patterns* · Kerievsky, *Refactoring to Patterns* · Feathers, *Working Effectively with Legacy Code* · Beck, *Tidy First?* · Metz, *99 Bottles of OOP*

### Every finding passes a gate

A finding is dropped unless all five hold:

1. It names a specific smell or complexity cost at a specific location.
2. The cost is **present tense** — someone reading or changing this code will pay it. Not "if we ever add another provider."
3. The proposed code is smaller or flatter than what it replaces, or it removes a real risk.
4. It adds no indirection whose only justification is future flexibility.
5. The author can do it now, without a rewrite.

Plus a counterweight list of things to argue *against*: interfaces with one implementation, config for a value that has never changed, a pattern that adds a class to remove an `if`, splitting a coherent function into single-use fragments whose names restate their bodies.

### "Considered and rejected" is mandatory

Every review ends with the things a reviewer might have flagged and why leaving them alone is right here. This is the section to read first. It forces the review to *show* restraint rather than claim it, and it's the fastest way to tell whether the model understood your code or is pattern-matching against the catalog.

### Severity means something specific

**Blocking** — will cause bugs or make the next change dangerous. Cleanliness alone is never blocking. **Worth doing** — pays for itself within this change. **Taste** — defensible either way, author's call.

Findings are capped at five, ordered by leverage. A review that manufactures twenty findings to look thorough trains you to ignore it.

---

## Notes for anyone forking this

**`context: fork` is deliberately off.** Running the skill in a forked subagent would keep the review out of your main context, but the fork can't see the conversation — so it couldn't review changes Claude just made in the same session, which is a big part of the point. If you'd rather have the isolation, add `context: fork` and `background: false` to the frontmatter.

**`effort: high` is set,** which overrides the session effort level while the skill is active. Design review is one of the places the extra reasoning actually pays; drop it if you disagree.

**These skills won't upload to claude.ai as-is.** The Agent Skills spec allows only six frontmatter fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). `craft` uses `argument-hint` and `effort`, which are Claude Code extensions, so packaging fails with an unexpected-key error rather than ignoring them. Strip those two fields for a claude.ai build. The `!` dynamic-context injection in `SKILL.md` also doesn't execute outside Claude Code.

**Tune it against your own diffs.** The gate and the counterweight list encode opinions about when abstraction is worth it, and those opinions should match your codebase. The [`skill-creator` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) will run a skill with and without itself across a set of real prompts so you can see whether an edit actually improved anything:

```bash
/plugin install skill-creator@claude-plugins-official
```

---

## License

MIT — see [LICENSE](LICENSE).
