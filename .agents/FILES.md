# AGENTS.md — FILES

Single source of truth for paths, config keys, and naming conventions.
Kept compact — agents hallucinate less when they know where definitions live.

## Pattern

- One file owns each class of definition (paths, config defaults, enums).
- Import from that file. Never hard-code values in other modules.
- Variables that address files get `_file` suffix; directories get `_dir`.

## Project-specific sources of truth

| What                   | Where                                                           | Key names                                       |
| ---------------------- | --------------------------------------------------------------- | ----------------------------------------------- |
| Package source root    | `src/sdo_skills_mcp/`  | `__init__.py`, `__about__.py` (version)         |
| CLI entry points       | `src/sdo_skills_mcp/cli/`            | `app.py` (Cyclopts app), `args.py`, `commands.py` |
| Catalog loader         | `src/sdo_skills_mcp/catalog.py`                                  | `SKILL_FILE`, `CATALOG_FILE`, `PROFILES_DIR`, `PACKAGE_DIR` |
| Skill layers           | `src/sdo_skills_mcp/catalog.toml`                                | layer name → list of skill ids                  |
| Profiles               | `src/sdo_skills_mcp/profiles/*.toml`                              | `id`, `title`, `description`, `include`         |
| MCP surface            | `src/sdo_skills_mcp/server.py`                                    | `build_server`, `sdo_list_skills`, `sdo_read_skill` |
| CLI environment        | `src/sdo_skills_mcp/cli/args.py`                                  | `ROOTS_ENV` (`SDO_SKILLS_ROOTS`)                |
| Test suite             | `tests/`                                                        | `test_*.py`, `conftest.py`                      |
| Project metadata       | `pyproject.toml`                                                | `[project]`, `[tool.pytest.ini_options]`        |
| Linter/formatter       | `ruff.toml`                                                     | Ruff rule selection, line length                |
| Type checker           | `ty.toml`                                                       | ty strictness                                   |
| Markdown linter        | `.config/rumdl.toml`                                            | `line-length`, `flavor`, disabled rules         |
| mise tasks             | `.config/mise/config.toml` + `.config/mise/conf.d/*.toml`       | `[tasks.dev]`, `[tasks.test]`, ...              |
| Copier answers         | `.copier-answers.yml`                                           | Template version + answers (regenerated)        |
| Pre-commit config      | `.pre-commit-config.yaml`                                       | Hook list                                       |

## Skill layout (external, not in this repo)

- `<root>/<layer>/<skill-id>/SKILL.md` — the skill entry point; the folder name
  must equal the frontmatter `name:` (FastMCP enforces this).
- `<root>/<layer>/<skill-id>/references/…` — extra files, addressed relative to the
  skill root (`references/procedures.md`, not `<skill-id>/references/…`).
- `Skill.files` values are **bytes** on the client side; the server decodes them with
  `_as_text` in `src/sdo_skills_mcp/server.py`.

## Naming conventions

- **Repository name** (`project_slug`): kebab-case (`my-project`)
- **Python package** (`package_slug`): snake_case (`my_project`)
- **Layout**: `src/sdo_skills_mcp/`
- **Test files**: `test_<module>.py`
- **Skill ids**: kebab-case (`etsi-governance`), matching the folder name
- **Template files** (in source template): `filename.ext.jinja` — the `.jinja`
  suffix is stripped on generation
