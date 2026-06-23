#!/usr/bin/env python3
"""
ANGEL community database — profile & index generator.

Reads data/people.json (+ data/organizations.json) and regenerates:
  - profiles/NN-slug.md   (one human-readable card per person)
  - INDEX.md              (summary table + tag rollups)

The JSON files are the source of truth. Edit those, then run:
    python3 generate.py
"""
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PROFILES = os.path.join(HERE, "profiles")

QLABELS = {
    "contribute": "Q2 · Qué puede aportar",
    "seeking": "Q3 · Qué busca actualmente",
    "wants_to_meet": "Q4 · A quién quiere conocer",
    "challenges": "Q5 · Tres principales desafíos",
    "goals_12mo": "Q6 · Qué resolvería en 12 meses",
    "projects": "Q7 · Proyecto / iniciativa",
}


def md_list(items):
    return "\n".join(f"- {x}" for x in items if x)


def write_profile(p):
    a = p["answers"]
    lines = []
    lines.append(f"# {p['name']}")
    if p.get("title"):
        lines.append(f"*{p['title']}*")
    lines.append("")
    lines.append(f"**País:** {p['country']['value']} ({p['country']['certainty']})  ")
    lines.append(f"**Rol:** {p['role']}  ")
    if p.get("organizations"):
        lines.append("**Organizaciones:** " + "; ".join(p["organizations"]) + "  ")
    if p.get("disease_focus"):
        lines.append("**Enfoque de enfermedad:** " + ", ".join(p["disease_focus"]) + "  ")
    lines.append(f"**Sector:** {', '.join(p['sector'])}  ")
    if p.get("contact"):
        lines.append(f"**Contacto:** {p['contact']}  ")
    lines.append(f"**Fuente:** {p['video']['file']} ({p['video']['timestamp_label']})")
    lines.append("")
    lines.append(f"> **Q1 · Relación con enfermedades raras:** {p['relationship']}")
    lines.append("")

    # Q2-Q4 (single text)
    for key in ("contribute", "seeking", "wants_to_meet"):
        val = a.get(key)
        if val:
            lines.append(f"**{QLABELS[key]}**  \n{val}")
            lines.append("")

    # Q5-Q6 (lists)
    for key in ("challenges", "goals_12mo"):
        val = a.get(key)
        if val:
            lines.append(f"**{QLABELS[key]}**")
            lines.append(md_list(val))
            lines.append("")

    # extra free message (e.g. Rodrigo)
    if a.get("message"):
        lines.append(f"**Mensaje:** {a['message']}")
        lines.append("")

    # Q7 projects
    projects = [pr for pr in a.get("projects", []) if pr.get("name") or pr.get("description")]
    if projects:
        lines.append(f"**{QLABELS['projects']}**")
        for pr in projects:
            name = pr.get("name") or "—"
            lines.append(f"- **{name}** — {pr.get('description', '')}")
        lines.append("")

    lines.append("## Matices (nuance)")
    lines.append(p["nuance"])
    lines.append("")

    if p.get("notable_quotes"):
        lines.append("## Citas")
        for q in p["notable_quotes"]:
            lines.append(f"> “{q}”")
            lines.append("")

    t = p["tags"]
    lines.append("## Tags")
    lines.append(f"`country:{t['country']}` " +
                 " ".join(f"`offers:{x}`" for x in t.get("offers", [])) + " " +
                 " ".join(f"`seeks:{x}`" for x in t.get("seeks", [])) + " " +
                 " ".join(f"`theme:{x}`" for x in t.get("themes", [])))
    lines.append("")

    fname = f"{p['id']:02d}-{p['slug']}.md"
    with open(os.path.join(PROFILES, fname), "w") as f:
        f.write("\n".join(lines))
    return fname


def write_index(people, orgs):
    lines = []
    lines.append("# ANGEL — Índice de la comunidad (CEPCAL 2026)\n")
    lines.append(f"{len(people)} personas · {len(orgs)} organizaciones · "
                 "fuente: 18 entrevistas (2026-06-21)\n")
    lines.append("> Generado por `generate.py`. No editar a mano: editar `data/*.json` y regenerar.\n")

    # Summary table
    lines.append("## Personas\n")
    lines.append("| # | Nombre | País | Rol | Enfoque | Perfil |")
    lines.append("|---|--------|------|-----|---------|--------|")
    for p in people:
        focus = ", ".join(p.get("disease_focus", [])) or "—"
        role_short = p["role"].split(";")[0][:60]
        link = f"profiles/{p['id']:02d}-{p['slug']}.md"
        lines.append(f"| {p['id']} | {p['name']} | {p['country']['value']} | "
                     f"{role_short} | {focus} | [ver]({link}) |")
    lines.append("")

    # Rollups
    by_country = Counter(p["country"]["value"] for p in people)
    lines.append("## Por país\n")
    for c, n in by_country.most_common():
        slugs = [p["name"] for p in people if p["country"]["value"] == c]
        lines.append(f"- **{c}** ({n}): {', '.join(slugs)}")
    lines.append("")

    theme_people = defaultdict(list)
    for p in people:
        for th in p["tags"].get("themes", []):
            theme_people[th].append(p["name"])
    lines.append("## Por tema (themes)\n")
    for th, names in sorted(theme_people.items(), key=lambda x: -len(x[1])):
        lines.append(f"- **{th}** ({len(names)}): {', '.join(names)}")
    lines.append("")

    # offers vs seeks — the matchmaking view
    lines.append("## Vista de emparejamiento (offers ↔ seeks)\n")
    offers = defaultdict(list)
    seeks = defaultdict(list)
    for p in people:
        for o in p["tags"].get("offers", []):
            offers[o].append(p["name"])
        for s in p["tags"].get("seeks", []):
            seeks[s].append(p["name"])
    lines.append("**Ofrecen:**")
    for o, names in sorted(offers.items(), key=lambda x: -len(x[1])):
        lines.append(f"- `{o}`: {', '.join(names)}")
    lines.append("\n**Buscan:**")
    for s, names in sorted(seeks.items(), key=lambda x: -len(x[1])):
        lines.append(f"- `{s}`: {', '.join(names)}")
    lines.append("")

    lines.append("## Organizaciones\n")
    lines.append("| Nombre | Tipo | País | Personas |")
    lines.append("|--------|------|------|----------|")
    for o in orgs:
        ppl = ", ".join(o.get("people_slugs", [])) or "—"
        lines.append(f"| {o['name']} | {o['type']} | {o['country']} | {ppl} |")
    lines.append("")

    with open(os.path.join(HERE, "INDEX.md"), "w") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(PROFILES, exist_ok=True)
    people = json.load(open(os.path.join(DATA, "people.json")))["people"]
    orgs = json.load(open(os.path.join(DATA, "organizations.json")))["organizations"]
    for p in people:
        write_profile(p)
    write_index(people, orgs)
    print(f"Generated {len(people)} profiles + INDEX.md")


if __name__ == "__main__":
    main()
