# craft

A design review for a diff. Not a correctness review — `/code-review` covers that.

```bash
/plugin marketplace add marcosjuncos11/skills
/plugin install craft@marcosjuncos-skills
```

## Usage

```bash
/craft                  # uncommitted work
/craft staged           # pre-commit gate
/craft branch           # everything since merge-base with main
/craft origin/develop   # against a ref
/craft app/vault/       # scope to a path
/craft pr 412           # via gh
```

Also triggers from plain language — "is this over-engineered?", "can this be simpler?" — including on changes Claude made earlier in the same session.

Proposes; does not edit. Tell it which findings to apply afterwards.

## Output

```
**Verdict:** one line

**Worth doing** — services/vault/checklist.py:88 — Information Leakage
Field order is encoded in both the serializer and the digest builder;
adding a column means editing both, and nothing says so.
<minimal diff>

**Considered and rejected**
- The 40-line `build_digest` — it reads top to bottom and splitting it
  would produce four single-use functions whose names restate their bodies.
```

**Blocking** means it will cause bugs or make the next change dangerous. Cleanliness alone is never blocking. Findings cap at five, ordered by leverage.

## How it decides

Six passes: complexity → smells → duplication → readability → patterns → seams. Patterns come fifth and may only be proposed for a pain an earlier pass located at a specific line, so the skill can't reach for `Strategy` where a dict of functions would do.

Every finding must clear a five-part gate, the sharpest clause being that the cost has to be **present tense** — "if we ever add another provider" is not a finding.

Ousterhout's complexity test arbitrates; Fowler's smell catalog supplies the vocabulary. See the [repo README](../../README.md#how-its-built) for why those two and not *Clean Code*'s line-count advice.

## Files

```
skills/craft/
├── SKILL.md              # procedure — stays in context once loaded
└── references/
    ├── complexity.md     # deep vs shallow modules, information leakage
    ├── smells.md         # Fowler's catalog: smell → tell → remedy
    └── patterns.md       # GoF, with a cheaper alternative for each
```
