# AGENTS.md — ONBOARDING

Read this when starting a new session. After first read, only revisit when
project structure or tooling changes significantly.

## Project

Serve the SDO writing skills (ETSI, 3GPP, ITU-T) over the Model Context Protocol.
One MCP server per writer profile (`etsi`, `3gpp`, `itut`); the host reads the skills
as resources or through two compat tools. Skill bodies live in `jr2804/sdo-skills` —
this repo owns the server, the profile composition, and the CLI. Full docs at
`README.md` or `docs/`.

## Quick start

```bash
mise dev        # install dependencies (uv sync --dev)
mise test       # run pytest with coverage
mise lint       # ruff + ty + codespell
mise format     # ruff format + isort + pyreorder
mise all        # test + lint + format in one pass

uv run sdo-skills-mcp profiles                   # list the profiles
uv run sdo-skills-mcp catalog --profile etsi     # list the skills of a profile
uv run sdo-skills-mcp check --root <skills>      # validate a real skills checkout
```

## Entry points (read these first)

| File / Section | Why |
| -------------- | --- |
| `AGENTS.md` | Root rail — rules + `.agents/` index |
| `.agents/POLICIES.md` | Boundaries, priorities, verification |
| `.agents/FILES.md` | Source-of-truth locations for this package |
| `.agents/HISTORY.md` | Past decisions and rationale |
| `src/sdo_skills_mcp/catalog.toml` | Skill layers — what the catalog knows |
| `src/sdo_skills_mcp/profiles/*.toml` | Profile composition — what a host serves |
| `pyproject.toml` | Dependencies, pytest config, build backend |
| `.copier-answers.yml` | Template answers (regenerated on `copier update`) |

## Layout

- **`src/sdo_skills_mcp/`** — primary package source (src layout)
- **`src/sdo_skills_mcp/cli/`** — Cyclopts CLI (`app.py`, `args.py`, `commands.py`)
- **`src/sdo_skills_mcp/catalog.toml`**, **`profiles/`** — layer and profile data
  (packaged as wheel artifacts)
- **`tests/`** — pytest suite (100% coverage gate)
- **`docs/`** — Zensical / MkDocs Material documentation
- **`.config/mise/`** — task runner config (`config.toml` + `conf.d/` fragments)

## CLI

| Command | Purpose |
| ------- | ------- |
| `serve` | Run the MCP server for one profile (`--profile`, `--root`, `--transport`, `--host`, `--port`) |
| `profiles` | List the available profiles |
| `catalog` | List the skills a profile serves |
| `check` | Validate every skill under the roots, report drift |

Roots come from `--root` (repeatable, first root wins) or from `SDO_SKILLS_ROOTS`
(`os.pathsep`-separated).

## Where to dig deeper

- `docs/` — user-facing documentation
- `.agents/HISTORY.md` — past decisions and rationale
- Source-tree AGENTS.md files — local contracts for each area

## Available tools

No MCP dev-features enabled. See `.copier-answers.yml` for template answers.
