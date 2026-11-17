# SDO Skills MCP

The standards-writing skills of the SDO Writer — ETSI, 3GPP, ITU-T — served over the
[Model Context Protocol](https://modelcontextprotocol.io), so an MCP host can read them
without copying them into every project.

<!-- markdownlint-disable MD033 -->
<p align="center">
  <a href="#"><img alt="Python 3.14+" src="https://img.shields.io/badge/python-3.14%2B-3776ab?logo=python"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="https://github.com/jr2804/sdo-skills-mcp/actions"><img alt="CI" src="https://github.com/jr2804/sdo-skills-mcp/actions/workflows/ci.yml/badge.svg"></a>
</p>
<!-- markdownlint-enable MD033 -->

The server exposes the skills through the MCP Skills extension (`skills/list`, `skills/get`,
`skill://<name>/SKILL.md` resources) and, for hosts that do not speak that extension yet,
through two plain tools: `sdo_list_skills` and `sdo_read_skill`.

Skill content is not in this repository. It lives in
[jr2804/sdo-skills](https://github.com/jr2804/sdo-skills); this package decides *which*
skills a profile serves and *how* they reach a host.

---

## Quick Start

```bash
# Clone and set up
git clone https://github.com/jr2804/sdo-skills-mcp.git
cd sdo-skills-mcp
mise dev
```

## Run it

```bash
uvx --from git+https://github.com/jr2804/sdo-skills-mcp sdo-skills-mcp serve \
  --profile etsi \
  --root ~/src/sdo-skills \
  --root ~/src/etsi-portal-tool
```

Roots are skill directories: every subdirectory that holds a `SKILL.md` is one skill.
Repeat `--root` to layer them; when two roots provide the same skill name the first wins.
Set `SDO_SKILLS_ROOTS` (path-list separated) instead of repeating the flag. Without either,
the server reads `./skills`.

## Profiles

| Profile | Skills | Content                                            |
| ------- | ------ | -------------------------------------------------- |
| `etsi`  | 11     | common + ETSI layers + the ETSI portal tooling     |
| `3gpp`  | 13     | common + the 3GPP layer                            |
| `itut`  | 7      | common + the ITU-T layer                           |

The composition is data, not code: `src/sdo_skills_mcp/catalog.toml` maps layer names to
skill names, `src/sdo_skills_mcp/profiles/<id>.toml` lists the layers a profile includes.
Adding a skill is a catalog edit; adding a profile is a new TOML file.

## Host configuration

OpenCode (`opencode.jsonc`) — works today, tools only:

```jsonc
{
  "mcp": {
    "sdo-skills": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/jr2804/sdo-skills-mcp", "sdo-skills-mcp",
                  "serve", "--profile", "etsi",
                  "--root", "/home/me/src/sdo-skills", "--root", "/home/me/src/etsi-portal-tool"],
      "enabled": true
    }
  }
}
```

Claude Code (`.mcp.json`) takes the same `command` array under `mcpServers`.
A host that implements the skills extension sees the skills natively; otherwise the two
tools carry the same content, one file at a time.

## Commands

| Command                       | Does                                                   |
| ----------------------------- | ------------------------------------------------------ |
| `serve --profile <id>`        | Serve a profile over stdio (default) or `--transport http` |
| `profiles`                    | List the profiles with their titles                     |
| `catalog --profile <id>`      | List the skills a profile serves, in order              |
| `check`                       | Validate every skill under the roots, flag catalog drift |

`check` is the gate to run against a checkout of the skills repository: it fails on invalid
frontmatter, on a folder without `SKILL.md`, and reports skills that `catalog.toml` names
but no root provides.

Shell completion (after the command is on your `PATH`):

```bash
sdo-skills-mcp --install-completion
```

## Development

```bash
mise dev        # uv sync -U --dev --all-extras --all-groups
mise test       # uv run pytest --cov=sdo_skills_mcp   (100 % coverage gate)
mise lint       # ruff + ty + codespell
mise format     # ruff format + pyreorder
mise all        # test + lint + spell + format + format-md + docs
```

A focused run needs `--no-cov` — the coverage gate fails below 100 % on a partial suite:

```bash
uv run pytest --no-cov tests/test_catalog.py
```

Pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

Documentation (Zensical):

```bash
mise docs-serve          # live preview at http://localhost:8000
mise docs-build          # build static site to site/
```

## Project Structure

```text
sdo-skills-mcp/
├── .config/mise/               # mise task definitions
├── .github/workflows/          # CI + release workflows
├── .agents/                    # DOX state files (onboarding, policies, history)
├── docs/                       # Zensical documentation
├── src/sdo_skills_mcp/
│   ├── __about__.py            # version metadata
│   ├── catalog.toml            # layer -> skill names
│   ├── profiles/*.toml         # profile -> layers
│   ├── catalog.py              # load, discover, select
│   ├── server.py               # FastMCP server, extension + compat tools
│   └── cli/                    # Cyclopts CLI (app, args, commands)
├── tests/                      # Test suite
├── .copier-answers.yml         # Template version tracking
├── pyproject.toml              # uv + hatch + pytest config
├── ruff.toml                   # Linter + formatter config
├── ty.toml                     # Type checker config
└── README.md
```

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Package manager | [uv](https://docs.astral.sh/uv/) | Fast installs, deterministic lockfile |
| Task runner | [mise](https://mise.jdx.dev/) | DAG-based tasks, tool version management |
| Linter + formatter | [ruff](https://docs.astral.sh/ruff/) | Single-binary code quality |
| Type checker | [ty](https://github.com/google/ty) | Strict type checking |
| Testing | [pytest](https://pytest.org/) | Test framework with 100% coverage gate |
| CLI | [Cyclopts](https://cyclopts.readthedocs.io/) | Type-driven CLI parsing and shell completion |
| Server | [FastMCP](https://gofastmcp.com/) | MCP server with the skills extension |
| Spell check | [codespell](https://github.com/codespell-project/codespell) | Code and doc spell checking |
| Documentation | [Zensical](https://github.com/zensical/zensical) | MkDocs Material with executable examples |
| Versioning | [uv-dynamic-versioning](https://github.com/ninoseki/uv-dynamic-versioning) | Git tag-based calendar versioning |
| Hooks | [pre-commit](https://pre-commit.com/) | Automated quality gate |
| CI/CD | GitHub Actions | Test matrix + calendar-version release |

## CI/CD

GitHub Actions runs on every push and PR:

| Workflow | Triggers | Jobs |
|----------|----------|------|
| **CI** (`ci.yml`) | push, PR to main | quality (ruff, ty, codespell) + test matrix (3.14, 3.15-dev on Linux/macOS/Windows) + docs build |
| **Release** (`release.yml`) | push to main | computes the next calendar version (`YYYY.MM.N`), tags the commit, builds the package, publishes a GitHub release with the artifacts |

## License

MIT — see [LICENSE](LICENSE) for details.

---

Generated from [copier-uv-plus](https://codeberg.org/jr2804/copier-uv-plus).
