"""Generate the deterministic strata of the eval set (seeded, reproducible).

    uv run python tests/eval/build_cases.py

Writes ``tests/eval/cases_generated.jsonl``. The paraphrase stratum is
written separately (by models, offline) into ``cases_paraphrase.jsonl``; the
two files together are the eval set.

Strata built here, each labelled by construction, never by the ranker:

* ``lexical`` — Kim & Croft-style known-item queries: 2-3 terms sampled by
  tf-idf from one note, plus one noise term from the corpus vocabulary.
* ``title`` — a note's title, verbatim: the exact-title guard (must be #1).
* ``relational`` — "which syntheses cite this?" (a source's terms; relevant =
  the topics that cite it) and "what supports this?" (a topic's terms;
  relevant = its sources) — labelled from the citation graph.
* ``negative`` — off-topic questions this brain holds no answer to.
* ``multilingual`` — non-English known-item queries.
"""

from __future__ import annotations

import json
import math
import random
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from brain_builder import build_brain  # noqa: E402

from brainkit.brain import _iter_notes, _own_body, _tokens, link_graph  # noqa: E402

SEED = 20261020
STOP = {
    "that",
    "this",
    "with",
    "from",
    "have",
    "been",
    "were",
    "their",
    "there",
    "they",
    "which",
    "would",
    "about",
    "into",
    "more",
    "also",
    "than",
    "these",
    "those",
    "other",
    "such",
    "when",
    "what",
    "will",
    "your",
    "over",
    "only",
    "most",
    "some",
    "each",
    "them",
    "then",
    "many",
    "like",
    "just",
    "very",
    "much",
    "does",
    "used",
    "using",
    "between",
    "both",
    "while",
    "where",
    "within",
    "without",
    "across",
    "could",
    "should",
    "after",
    "before",
    "being",
    "under",
    "make",
    "made",
    "because",
    "through",
    "same",
    "well",
    "even",
    "here",
    "http",
    "https",
    "www",
    "com",
    "html",
}

NEGATIVES = [
    "sourdough starter hydration ratio",
    "baroque harpsichord temperament tuning",
    "coral reef bleaching water temperature",
    "marathon taper week mileage",
    "medieval tapestry natural dyes",
    "volcanic basalt columns cooling",
    "cat litter odor control",
    "tennis serve continental grip",
    "knitting cable stitch chart",
    "home office tax deduction rules",
    "orchid repotting bark mix",
    "espresso grind size channeling",
]

# (query, url tail of the note that answers it). The two synthetic runs land
# in different splits, so non-English search is measured on both. The
# kör/kor pair is the accent-folding collision probe (decision on folding).
MULTILINGUAL = [
    ("한국어 출처 링크", "geomsaek"),
    ("kör gráf erdő", "kor-graf"),
    ("kor emlékezet", "kor-emlekezet"),
    ("szövegösszefoglaló modellek hibái", "tudasbazis"),
    ("szovegosszefoglalo tudasbazis", "tudasbazis"),
    ("Gedächtnis Notizen ersetzt", "gedaechtnis"),
    ("知识库 来源链接", "zhishiku"),
    ("出典 見出し", "kensaku"),
    ("mémoire provenance synthèse", "memoire"),
]


def family_of(meta: dict[str, str]) -> str:
    projects = meta.get("projects", "")
    if projects.startswith("["):
        first = json.loads(projects)
        if first:
            return str(first[0]).split("/")[0] + "/" + str(first[0]).split("/")[-1]
    project = meta.get("project", "")
    return project.split("/")[0] + "/" + project.split("/")[-1] if project else ""


def good(term: str) -> bool:
    return len(term) >= 4 and term.isalpha() and term not in STOP


def main() -> None:
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as tmp:
        brain = build_brain(Path(tmp))

        # Sampling pools exclude the synthetic runs, so adding a probe note
        # never reshuffles the seeded lexical/title/relational cases.
        def real(note_meta: dict[str, str]) -> bool:
            return "multilingual" not in family_of(note_meta)

        notes = [
            (path, note)
            for path, note in _iter_notes(brain)
            if len(_own_body(note)) > 400 and real(note.meta)
        ]
        all_notes = _iter_notes(brain)
        real_notes = [(p, n) for p, n in all_notes if real(n.meta)]
        bags = {
            path.stem: Counter(t for t in _tokens(_own_body(n)) if good(t))
            for path, n in real_notes
        }
        df: Counter[str] = Counter()
        for bag in bags.values():
            df.update(bag.keys())
        total = len(bags)
        vocab = [t for t, n in df.items() if 3 <= n <= total * 0.3]

        def top_terms(slug: str, limit: int = 25) -> list[str]:
            bag = bags[slug]
            scored = {
                t: tf * math.log(total / df[t])
                for t, tf in bag.items()
                if df[t] <= total * 0.2
            }
            return [
                t for t, _s in sorted(scored.items(), key=lambda kv: -kv[1])[:limit]
            ]

        cases: list[dict[str, object]] = []

        def add(
            stratum: str, query: str, relevant: list[str], family: str, **extra: object
        ) -> None:
            cases.append(
                {
                    "id": f"{stratum[:3]}-{len([c for c in cases if c['stratum'] == stratum]) + 1:03d}",
                    "query": query,
                    "relevant": relevant,
                    "stratum": stratum,
                    "family": family,
                    "split": "",
                    **extra,
                }
            )

        sample = rng.sample(notes, min(60, len(notes)))
        for path, note in sample:
            terms = top_terms(path.stem)
            if len(terms) < 4:
                continue
            k = rng.choice((2, 3))
            weights = [len(terms) - i for i in range(len(terms))]
            picked: list[str] = []
            while len(picked) < k:
                term = rng.choices(terms, weights=weights)[0]
                if term not in picked:
                    picked.append(term)
            picked.append(rng.choice(vocab))
            rng.shuffle(picked)
            add("lexical", " ".join(picked), [path.stem], family_of(note.meta))

        titled = [
            (p, n)
            for p, n in real_notes
            if n.meta.get("type") in ("source", "report") and len(n.title.split()) >= 4
        ]
        for path, note in rng.sample(titled, 10):
            # The WHOLE title: a truncated one cannot test exact-title rank.
            add("title", note.title, [path.stem], family_of(note.meta))

        outgoing, incoming = link_graph(brain)
        kinds = {p.stem: n.meta.get("type", "") for p, n in all_notes}
        metas = {p.stem: n.meta for p, n in all_notes}
        cited = [
            slug
            for slug, kind in sorted(kinds.items())
            if kind == "source"
            and real(metas[slug])
            and any(kinds.get(s) == "topic" for s in incoming.get(slug, ()))
            and len(top_terms(slug)) >= 2
        ]
        for slug in rng.sample(cited, min(10, len(cited))):
            topics = sorted(s for s in incoming[slug] if kinds.get(s) == "topic")
            add(
                "relational",
                " ".join(top_terms(slug)[:2]),
                topics,
                family_of(metas[slug]),
                required=topics,
            )
        topic_slugs = [
            s
            for s, k in sorted(kinds.items())
            if k == "topic" and real(metas[s]) and len(top_terms(s)) >= 3
        ]
        for slug in rng.sample(topic_slugs, min(10, len(topic_slugs))):
            # Only the topic's own family's sources: a source shared with
            # another run would put the same evidence in both splits.
            sources = sorted(
                t
                for t in outgoing.get(slug, ())
                if kinds.get(t) == "source"
                and family_of(metas[t]) == family_of(metas[slug])
            )
            if sources:
                add(
                    "relational",
                    " ".join(top_terms(slug)[:3]),
                    sources,
                    family_of(metas[slug]),
                )

        for query in NEGATIVES:
            add("negative", query, [], "negative", negative=True)

        by_url = {
            n.meta.get("url", "").split("/")[-1]: p.stem
            for p, n in all_notes
            if n.meta.get("type") == "source"
        }
        for query, url_tail in MULTILINGUAL:
            slug = by_url[url_tail]
            add("multilingual", query, [slug], family_of(metas[slug]))

    # Split by research-run family so near-duplicate evidence never straddles
    # dev and held-out. A case's family is its EVIDENCE's family (the first
    # relevant note's run), the paraphrase cases are re-split with the same
    # map, and families alternate in sorted order (hashing six clustered
    # them). Negatives alternate case by case.
    paraphrase_path = HERE / "cases_paraphrase.jsonl"
    paraphrases = [
        json.loads(line)
        for line in paraphrase_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    everything = cases + paraphrases
    families = sorted({str(c["family"]) for c in everything} - {"negative"})
    real_families = [f for f in families if "multilingual" not in f]
    assignment = {f: ("dev", "heldout")[i % 2] for i, f in enumerate(real_families)}
    synthetic = sorted(f for f in families if "multilingual" in f)
    assignment.update({f: ("dev", "heldout")[i % 2] for i, f in enumerate(synthetic)})
    negatives = 0
    for case in everything:
        if case["family"] == "negative":
            case["split"] = ("dev", "heldout")[negatives % 2]
            negatives += 1
        else:
            case["split"] = assignment[str(case["family"])]
    splits_of: dict[str, set[str]] = {}
    for case in everything:
        for slug in [*case.get("relevant", []), *case.get("required", [])]:
            splits_of.setdefault(str(slug), set()).add(str(case["split"]))
    leaked = sorted(slug for slug, found in splits_of.items() if len(found) > 1)
    if leaked:
        raise SystemExit(f"evidence straddles dev/held-out: {leaked}")

    for path, rows in (
        (HERE / "cases_generated.jsonl", cases),
        (paraphrase_path, paraphrases),
    ):
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
    print(f"{len(cases)} generated + {len(paraphrases)} paraphrase cases")


if __name__ == "__main__":
    main()
