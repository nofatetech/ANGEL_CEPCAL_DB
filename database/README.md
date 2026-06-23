# ANGEL — Base de datos de la comunidad (CEPCAL 2026)

Base de datos estructurada de las personas y entidades entrevistadas en el congreso
centroamericano de enfermedades raras **CEPCAL 2026** (grabaciones del 2026-06-21).
Objetivo de largo plazo: **hacer crecer y conectar la comunidad de enfermedades raras**
en la región — por eso el dato está pensado para *emparejar* personas (quién ofrece
qué ↔ quién busca qué), no solo para archivarlas.

## Estructura

```
database/
├── data/
│   ├── people.json          # FUENTE DE VERDAD — 19 personas, respuestas + matices + tags
│   └── organizations.json   # 15 organizaciones/entidades, enlazadas a personas
├── profiles/                # 1 ficha .md por persona (GENERADO — no editar a mano)
├── INDEX.md                 # tabla resumen + rollups por país/tema + vista de emparejamiento (GENERADO)
├── generate.py              # regenera profiles/ e INDEX.md desde data/*.json
└── README.md
```

**Flujo de trabajo:** editar `data/*.json` → ejecutar `python3 generate.py` → se
regeneran `profiles/` e `INDEX.md`. Nunca editar los `.md` generados a mano.

## Idioma

Nombres de campos y tags en **inglés**; el contenido (citas, respuestas, matices) en
**español original**, verbatim y ligeramente limpiado de muletillas.

## El cuestionario (7 preguntas)

Casi todas las entrevistas siguen el mismo guion, lo que permite la extracción
estructurada. Ver `data/people.json → meta.questionnaire`.

1. ¿Quién eres y cuál es tu relación con las enfermedades raras?
2. ¿Qué puedes aportar a esta comunidad?
3. ¿Qué estás buscando actualmente?
4. ¿Qué tipo de personas u organizaciones te gustaría conocer?
5. Tres principales desafíos en tu país/comunidad.
6. Tres problemas a resolver en los próximos 12 meses.
7. Un proyecto/iniciativa/recurso para compartir.

> Dos clips se salen del guion: **Rodrigo** (paciente, entrevista corta) y el clip de
> **Ángel** (presentación de la organización, orador no identificado).

## Esquema de cada persona (`people.json`)

| Campo | Significado |
|-------|-------------|
| `id`, `slug` | identificador numérico y textual |
| `name`, `title` | nombre y tratamiento (Dr./Lcda./…) |
| `video` | archivo de origen + timestamp del nombre del clip |
| `country` | `{value, certainty}` — `stated` (lo dijo) o `inferred` (deducido del contexto) |
| `role`, `organizations`, `sector` | rol, entidades y clasificación de sector |
| `relationship` | respuesta a Q1 |
| `disease_focus` | enfermedades/áreas mencionadas |
| `answers` | `contribute, seeking, wants_to_meet, challenges[], goals_12mo[], projects[]` (Q2–Q7) |
| `contact` | datos de contacto si se mencionaron |
| `nuance` | **texto libre con el matiz individual**: su ángulo, personalidad, por qué es un nodo útil en la red |
| `notable_quotes` | citas verbatim destacadas |
| `tags` | `country`, `sectors[]`, `offers[]`, `seeks[]`, `themes[]` — base del emparejamiento |

## Cómo usar para emparejar (matchmaking)

`INDEX.md` incluye una **vista de emparejamiento** que cruza `offers` ↔ `seeks`.
Ejemplos detectados en esta primera tanda:

- **Registros / bases de datos:** Marco Tulio Páez (busca *ingeniería* y diseña una ficha
  clínica), Valte Rosales (*efecto red*, Galenus), Cris Peláez (*registro latinoamericano*,
  metodología) y Melissa Montenegro (*datos*, soberanía de datos) convergen en lo mismo →
  candidatos a un grupo de trabajo de **registro/datos**.
- **Ley y políticas:** Suset Bour, Marco Tulio Páez (Guatemala, sin ley), Ana Amato,
  Juan Carlos Villalta (Costa Rica) → bloque de **incidencia legislativa**.
- **Mentoría de asociaciones:** Yanina Argueta / Creciendo con Diabetes (20 años) puede
  acompañar a fundadoras emergentes como Patricia Morales (FQ) y Claribel Castillo (Rett).
- **Expansión regional:** Carlos Sánchez quiere replicar el congreso en Rep. Dominicana;
  Honduras (Leslie López, Jorge Sosa) aún sin ley → frentes de crecimiento de la red.

## Cobertura

- 7 países: Guatemala (9), México (3), Costa Rica (2), Honduras (2), El Salvador (1),
  Rep. Dominicana (1), Nicaragua (1).
- Sectores: genetistas clínicos, fundadoras de asociaciones de pacientes, un paciente
  (Rodrigo, Duchenne), nutrición, microbiología, health-tech (Galenus, Capris/Illumina),
  investigación académica (Cris Peláez), salud pública (Carlos Sánchez).

## Pendientes / a confirmar (`TODO`)

- **Clip de Ángel (2.36.51):** identificar al orador y a "Andrea"; definir si Ángel es la
  organización-paraguas de este proyecto.
- ~~Nombre canónico del evento~~ → **confirmado: CEPCAL** (el ASR lo transcribe como
  CERCAL / SECALPA / "Central").
- **FECPAC:** confirmar denominación y su relación con CEPCAL/ANGEL.
- **Países `inferred`:** confirmar país de Patricia Morales y José Elías García Ortiz.
- **Nombres de asociaciones** sin denominación oficial (FQ de Patricia Morales; programa de RD).
- **Contactos:** las entrevistas casi no capturan email/teléfono/redes. Para una base de
  datos de comunidad accionable conviene una segunda pasada de datos de contacto.

## Extender la base con nuevas entrevistas

1. Transcribir el nuevo clip (los `.mp4.txt` son la versión canónica).
2. Añadir un objeto al array `people` en `data/people.json` (copiar la estructura de uno
   existente; respetar el vocabulario de tags para que el emparejamiento funcione).
3. Añadir/enlazar organizaciones en `data/organizations.json`.
4. `python3 generate.py`.
