#!/usr/bin/env python3
"""
ANGEL community database — profile & index generator (Obsidian-native).

Reads data/people.json (+ data/organizations.json) and regenerates:
  - profiles/NN-slug.md   (one card per person, with YAML frontmatter)
  - orgs/<org-id>.md      (one note per organization)
  - themes/<theme>.md     (one concept node per theme — the matchmaking axis)
  - INDEX.md              (summary table + tag rollups)

The JSON files are the source of truth. Edit those, then run:
    python3 generate.py

Obsidian conventions emitted here (all from JSON, never hand-add to .md):
  - Frontmatter "properties" power filtering, the Properties UI, and Dataview.
  - Wikilinks INSIDE frontmatter (orgs:, themes:) create real graph edges while
    keeping the body clean. Person<->org edges draw the community network;
    person<->theme edges cluster people by shared concern = the matchmaking map.
  - Nested tags (offers/x, seeks/y) give plugin-free tag-pane browsing of who
    offers / seeks what. (offers and seeks use disjoint vocabularies, so they are
    tags/properties, NOT shared link-nodes — themes are the shared axis.)
"""
import json
import os
import glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PROFILES = os.path.join(HERE, "profiles")
ORGS = os.path.join(HERE, "orgs")
THEMES = os.path.join(HERE, "themes")

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


def yq(s):
    """Safely double-quote a scalar for YAML frontmatter."""
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def fm_scalar(key, val):
    return [f"{key}: {yq(val)}"]


def fm_list(key, items):
    out = [f"{key}:"]
    out.extend(f"  - {yq(it)}" for it in items)
    return out


def org_link(org_id, name):
    return f"[[orgs/{org_id}|{name}]]"


def theme_link(theme):
    return f"[[themes/{theme}|{theme}]]"


def person_link(p):
    return f"[[profiles/{p['id']:02d}-{p['slug']}|{p['name']}]]"


def write_profile(p, slug2orgs):
    a = p["answers"]
    t = p["tags"]
    org_refs = slug2orgs.get(p["slug"], [])  # list of (org_id, org_name)

    # ---- frontmatter (properties + graph edges) ----
    fm = ["---"]
    fm += [f"id: {p['id']}"]
    fm += fm_scalar("name", p["name"])
    if p.get("title"):
        fm += fm_scalar("title", p["title"])
    fm += fm_scalar("country", p["country"]["value"])
    fm += fm_scalar("country_certainty", p["country"]["certainty"])
    fm += fm_scalar("role", p["role"])
    if p.get("sector"):
        fm += fm_list("sectors", p["sector"])
    if p.get("disease_focus"):
        fm += fm_list("disease_focus", p["disease_focus"])
    if org_refs:
        fm += fm_list("orgs", [org_link(oid, name) for oid, name in org_refs])
    if t.get("offers"):
        fm += fm_list("offers", t["offers"])
    if t.get("seeks"):
        fm += fm_list("seeks", t["seeks"])
    if t.get("themes"):
        fm += fm_list("themes", [theme_link(th) for th in t["themes"]])
    fm += fm_scalar("video", p["video"]["file"])
    fm += fm_scalar("source_timestamp", p["video"]["timestamp_label"])
    tags = ["person"]
    tags += [f"offers/{x}" for x in t.get("offers", [])]
    tags += [f"seeks/{x}" for x in t.get("seeks", [])]
    fm += fm_list("tags", tags)
    fm += ["---", ""]

    # ---- readable body ----
    lines = list(fm)
    lines.append(f"# {p['name']}")
    if p.get("title"):
        lines.append(f"*{p['title']}*")
    lines.append("")
    lines.append(f"**País:** {p['country']['value']} ({p['country']['certainty']})  ")
    lines.append(f"**Rol:** {p['role']}  ")
    if org_refs:
        lines.append("**Organizaciones:** " +
                     "; ".join(org_link(oid, name) for oid, name in org_refs) + "  ")
    if p.get("disease_focus"):
        lines.append("**Enfoque de enfermedad:** " + ", ".join(p["disease_focus"]) + "  ")
    lines.append(f"**Sector:** {', '.join(p['sector'])}  ")
    if p.get("contact"):
        lines.append(f"**Contacto:** {p['contact']}  ")
    lines.append(f"**Fuente:** {p['video']['file']} ({p['video']['timestamp_label']})")
    lines.append("")
    lines.append(f"> **Q1 · Relación con enfermedades raras:** {p['relationship']}")
    lines.append("")

    for key in ("contribute", "seeking", "wants_to_meet"):
        val = a.get(key)
        if val:
            lines.append(f"**{QLABELS[key]}**  \n{val}")
            lines.append("")

    for key in ("challenges", "goals_12mo"):
        val = a.get(key)
        if val:
            lines.append(f"**{QLABELS[key]}**")
            lines.append(md_list(val))
            lines.append("")

    if a.get("message"):
        lines.append(f"**Mensaje:** {a['message']}")
        lines.append("")

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


def write_org(o, slug2person):
    lines = ["---"]
    lines += fm_scalar("name", o["name"])
    lines += fm_scalar("type", o["type"])
    lines += fm_scalar("country", o["country"])
    lines += fm_list("tags", ["org"])
    lines += ["---", ""]
    lines.append(f"# {o['name']}")
    lines.append("")
    lines.append(f"**Tipo:** {o['type']}  ")
    lines.append(f"**País:** {o['country']}")
    lines.append("")
    if o.get("description"):
        lines.append(o["description"])
        lines.append("")
    people = [slug2person[s] for s in o.get("people_slugs", []) if s in slug2person]
    if people:
        lines.append("## Personas")
        for p in people:
            lines.append(f"- {person_link(p)}")
        lines.append("")
    if o.get("related_people_mentioned"):
        lines.append("## Mencionadas (sin perfil)")
        lines.append(", ".join(o["related_people_mentioned"]))
        lines.append("")
    if o.get("notes"):
        lines.append("## Notas")
        lines.append(o["notes"])
        lines.append("")
    with open(os.path.join(ORGS, f"{o['id']}.md"), "w") as f:
        f.write("\n".join(lines))


def write_theme(theme, people):
    lines = ["---"]
    lines += fm_scalar("name", theme)
    lines += fm_list("tags", ["theme"])
    lines += ["---", ""]
    lines.append(f"# {theme}")
    lines.append("")
    lines.append(f"*Tema compartido — {len(people)} persona(s). "
                 "Tablero de emparejamiento: quién ofrece y quién busca en torno a este tema.*")
    lines.append("")
    lines.append("| Persona | País | Ofrece | Busca |")
    lines.append("|---|---|---|---|")
    for p in people:
        t = p["tags"]
        offers = ", ".join(t.get("offers", [])) or "—"
        seeks = ", ".join(t.get("seeks", [])) or "—"
        lines.append(f"| {person_link(p)} | {p['country']['value']} | {offers} | {seeks} |")
    lines.append("")
    with open(os.path.join(THEMES, f"{theme}.md"), "w") as f:
        f.write("\n".join(lines))


def write_home(people, orgs, theme_people):
    lines = []
    lines.append("# 🏠 ANGEL — Inicio")
    lines.append("")
    lines.append(f"*{len(people)} personas · {len(orgs)} organizaciones · "
                 f"{len(theme_people)} temas · CEPCAL 2026 (2026-06-21)*")
    lines.append("")
    lines.append("Base de datos viva de la comunidad centroamericana de enfermedades raras. "
                 "El objetivo es **conectar** personas, no solo archivarlas.")
    lines.append("")

    lines.append("## Cómo navegar")
    lines.append("- **Grafo** (Ctrl/Cmd-G): los nodos dorados son **temas** (los conectores), "
                 "verdes **organizaciones**, azules **personas** (naranja = país inferido, por confirmar).")
    lines.append("- **Panel de etiquetas**: despliega `offers/` y `seeks/` para ver quién ofrece / busca qué.")
    lines.append("- [[INDEX|Índice completo]] · tablas de personas, países y emparejamiento.")
    lines.append("")

    lines.append("## Temas (tableros de emparejamiento)")
    lines.append("Cada tema lista quién **ofrece** y quién **busca** a su alrededor.")
    lines.append("")
    for th, ppl in sorted(theme_people.items(), key=lambda x: -len(x[1])):
        lines.append(f"- [[themes/{th}|{th}]] ({len(ppl)})")
    lines.append("")

    lines.append("## Organizaciones")
    for o in orgs:
        lines.append(f"- [[orgs/{o['id']}|{o['name']}]]")
    lines.append("")

    # data-derived open TODOs (keeps the worklist honest as data grows)
    inferred = [p for p in people if p["country"]["certainty"] == "inferred"]
    no_contact = [p for p in people if not p.get("contact")]
    unidentified = [p for p in people if "unidentified" in p["slug"]]
    lines.append("## Pendientes (derivado de los datos)")
    lines.append(f"- **País por confirmar** ({len(inferred)}): " +
                 ", ".join(person_link(p) for p in inferred) if inferred else "- País por confirmar: ninguno")
    lines.append(f"- **Sin contacto** ({len(no_contact)}): " +
                 ", ".join(person_link(p) for p in no_contact) if no_contact else "- Sin contacto: ninguno")
    if unidentified:
        lines.append(f"- **Sin identificar** ({len(unidentified)}): " +
                     ", ".join(person_link(p) for p in unidentified))
    lines.append("")

    with open(os.path.join(HERE, "HOME.md"), "w") as f:
        f.write("\n".join(lines))


def write_index(people, orgs):
    lines = []
    lines.append("# ANGEL — Índice de la comunidad (CEPCAL 2026)\n")
    lines.append(f"{len(people)} personas · {len(orgs)} organizaciones · "
                 "fuente: 18 entrevistas (2026-06-21)\n")
    lines.append("> Generado por `generate.py`. No editar a mano: editar `data/*.json` y regenerar.\n")

    lines.append("## Personas\n")
    lines.append("| # | Nombre | País | Rol | Enfoque | Perfil |")
    lines.append("|---|--------|------|-----|---------|--------|")
    for p in people:
        focus = ", ".join(p.get("disease_focus", [])) or "—"
        role_short = p["role"].split(";")[0][:60]
        link = f"[[profiles/{p['id']:02d}-{p['slug']}|ver]]"
        lines.append(f"| {p['id']} | {p['name']} | {p['country']['value']} | "
                     f"{role_short} | {focus} | {link} |")
    lines.append("")

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
        lines.append(f"- [[themes/{th}|{th}]] ({len(names)}): {', '.join(names)}")
    lines.append("")

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
        lines.append(f"| [[orgs/{o['id']}|{o['name']}]] | {o['type']} | {o['country']} | {ppl} |")
    lines.append("")

    with open(os.path.join(HERE, "INDEX.md"), "w") as f:
        f.write("\n".join(lines))


def clean_generated(folder):
    for f in glob.glob(os.path.join(folder, "*.md")):
        os.remove(f)


def main():
    for d in (PROFILES, ORGS, THEMES):
        os.makedirs(d, exist_ok=True)
    people = json.load(open(os.path.join(DATA, "people.json")))["people"]
    orgs = json.load(open(os.path.join(DATA, "organizations.json")))["organizations"]

    slug2person = {p["slug"]: p for p in people}
    slug2orgs = defaultdict(list)
    for o in orgs:
        for s in o.get("people_slugs", []):
            slug2orgs[s].append((o["id"], o["name"]))

    theme_people = defaultdict(list)
    for p in people:
        for th in p["tags"].get("themes", []):
            theme_people[th].append(p)

    # rebuild generated link-target folders (orgs/themes are generator-owned)
    clean_generated(PROFILES)
    clean_generated(ORGS)
    clean_generated(THEMES)

    for p in people:
        write_profile(p, slug2orgs)
    for o in orgs:
        write_org(o, slug2person)
    for th, ppl in theme_people.items():
        write_theme(th, ppl)
    write_index(people, orgs)
    write_home(people, orgs, theme_people)
    print(f"Generated {len(people)} profiles, {len(orgs)} orgs, "
          f"{len(theme_people)} theme nodes + INDEX.md + HOME.md")


if __name__ == "__main__":
    main()
