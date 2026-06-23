# ANGEL_CEPCAL_DB

Structured database of the rare-disease (*enfermedades raras*) community interviewed at the
**CEPCAL 2026** congress (Central America, recorded 2026-06-21). A long-term effort to grow
and connect the regional community by capturing who people are, what they offer, and what
they're looking for — so they can be matched to one another.

## Contents

- **[`database/`](database/)** — the database and its docs ([README](database/README.md),
  [INDEX](database/INDEX.md)).
  - `database/data/people.json` + `organizations.json` — **source of truth** (19 people, 15 orgs).
  - `database/profiles/` — one Markdown card per person (generated).
  - `database/generate.py` — regenerates profiles + index from the JSON.
- **`Videos_CEPCAL_2026/transcript/`** — the 18 canonical interview transcripts (the raw data).

Raw `.mp4` videos and the source `.zip` are kept local (gitignored) — see
[`database/README.md`](database/README.md) for the schema, conventions, and how to extend.
