# 🗺️ ANGEL — Backlog & plan

*Documento vivo, mantenido a mano (no lo genera `generate.py`). Filosofía: simple pero útil,
80% útil / 20% bonito. Lo que de verdad importa es **conectar** personas.*

Prioridad: **Now** (esta semana) · **Next** (próximas) · **Later** (cuando haya tiempo) ·
**Ideas** (sin compromiso).

---

## Now — calidad de los datos (la base de todo)
Estos son los huecos que más debilitan el emparejamiento y el grafo.

- [ ] **Confirmar nombre del congreso**: CEPCAL vs CERCAL / SECALPA (ruido de transcripción ASR).
- [ ] **Identificar al/la presentador/a de "Ángel"** (clip 2.36.51) y a **"Andrea"** (mencionada).
- [ ] **Confirmar 9 países `inferred`** → ver [[HOME#Pendientes (derivado de los datos)]].
      Cambiar `country.certainty` a `stated` en `data/people.json` al confirmar.
- [ ] **Capturar contactos** (17 sin contacto): email / teléfono / red social, con consentimiento.
- [ ] **Confirmar nombres de organizaciones** sin denominación exacta:
      `org-fq` (Asociación de Fibrosis Quística), `org-fecpac` (relación con CEPCAL/ANGEL).

## Next — calidad del emparejamiento
- [ ] **Afinar `SEEK_BRIDGE`** (en `generate.py`) contra los transcripts reales — revisar que
      cada puente `seek → offer` tenga sentido; añadir los que falten.
- [ ] **Normalizar vocabulario de tags** `offers`/`seeks` en origen para que los matches 1:1
      sean más limpios (hoy los vocabularios son casi disjuntos; por eso existe el puente).
- [ ] **Cubrir la necesidad `funding`** → ver [[MATCHES#⚠️ Necesidades no cubiertas]].
      Nadie ofrece financiamiento: identificar y sumar donantes / fundaciones / cooperación.
- [ ] **Marcar matches accionados** — cuando dos personas efectivamente se conectan, registrarlo
      (campo nuevo o tag) para no re-sugerir lo mismo.

## Later — herramientas y vault
- [ ] **Dataview** (1 plugin) → `Matchmaking.md` con tablas vivas que se recalculan solas.
      Alternativa "en app" a `MATCHES.md` generado. Ver explicación en el historial del proyecto.
- [ ] **Fijar `HOME.md` como página de inicio** (Bookmarks / plugin Homepage).
- [ ] **Enlaces a video** — vincular cada perfil a su clip / timestamp (los `.mp4` quedan locales,
      no en el repo; ver `.gitignore`).
- [ ] **Capa org ↔ org** — relaciones entre CEPCAL / FECPAC / Ángel y demás.
- [ ] **Color por país o sector** en el grafo (grupos de color adicionales), si aporta claridad.

## Ideas — sin compromiso
- Plantilla de **alta de personas** para sumar gente después del evento (formulario → JSON).
- **Multi-evento**: añadir campo `event` y `schema_version` para futuros congresos en la misma base.
- **Vista pública / compartible** (Obsidian Publish o sitio estático) cuidando privacidad.
- **Mapa geográfico** Centroamérica (plugin de mapas) con los nodos por país.
- Revisión de **consentimiento / privacidad**: qué es público en GitHub y qué no (contactos).

---

## Done
- ✅ Base JSON + perfiles Markdown (fuente de verdad en `data/*.json`).
- ✅ Vault Obsidian nativo: frontmatter, wikilinks en frontmatter (aristas del grafo).
- ✅ Notas de organización (`orgs/`) y nodos de tema (`themes/`) como eje de emparejamiento.
- ✅ Grafo con grupos de color por tipo de nodo (tema / org / persona; naranja = país inferido).
- ✅ `themes/*.md` como tableros de emparejamiento (Persona · País · Ofrece · Busca).
- ✅ `HOME.md` (MOC + pendientes derivados de los datos).
- ✅ `MATCHES.md` — sugerencias de contacto vía `SEEK_BRIDGE` + necesidades no cubiertas.
- ✅ Config curada de `.obsidian` versionada; `workspace.json` ignorado.
