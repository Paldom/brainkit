# Keeping a brain in Git

A brain is plain markdown, so Git is its history, its review gate and its sync.
A few settings make that smooth.

## `.gitattributes` for the brain directory

```gitattributes
# The journal is append-mostly: let concurrent branches both keep their lines.
brain/log.md            merge=union
# Generated maps: never hand-merge them; regenerate after a merge instead.
brain/**/index.md       -merge
brain/llms.txt          -merge
brain/manifest.json     -merge
# Machine state, rebuildable from the notes.
brain/.brainkit/        export-ignore
```

After a merge that touched notes, regenerate what brainkit owns:

```bash
brainkit --brain brain rebuild    # frontmatter encoding, counts, every index
brainkit --brain brain lint
```

`brain/.brainkit/` (the writer lock and the token cache) writes its own
`.gitignore`; nothing in it needs committing.

## A CI gate for a team brain

```yaml
# .github/workflows/brain.yml
name: brain
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv tool install brainkit
      # Nothing brainkit derives may drift from the notes...
      - run: brainkit --brain brain rebuild && git diff --exit-code
      # ...and the brain must be structurally sound. Pin the clock so the
      # check cannot turn red without a commit.
      - run: brainkit --brain brain lint --as-of 2026-10-20
```

`lint` exits 1 on errors only; warnings (stale notes, ungrounded literals,
suspicious content, near-duplicates) are advisory unless you add
`--warnings-as-errors`.

## Reviewing what agents write

- Agents write through `brainkit ingest-notes` only; open a pull request per
  batch so a human reviews the diff before it becomes knowledge.
- A reviewer who checked a note records it in the note itself:
  `verified: [{"by": "human:<you>", "at": "2026-10-20T00:00:00Z"}]`. An
  unverified agent-written note (`derived_from` without a human `verified`)
  ranks without the synthesis bonus and is labelled `derived`.
- Sign commits on team brains (`git config commit.gpgsign true`, or
  [gitsign](https://github.com/sigstore/gitsign)) so the history says who
  vouched for what.
- `brainkit ingest-notes --expect-digest <sha>` refuses an update when the note
  changed since the agent read it — the same compare-and-swap a reviewer relies
  on when two agents edit one note.
