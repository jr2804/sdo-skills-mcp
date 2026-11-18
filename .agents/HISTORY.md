# AGENTS.md — HISTORY

Recorded decisions with git references. Read when relevant to current task.
Acts as simple long-term memory for the project.

## Format

| Date       | Decision   | Rationale   | Git ref          |
| ---------- | ---------- | ----------- | ---------------- |
| YYYY-MM-DD | [describe] | [why]       | [commit hash/tag] |

## Guidance

- Record decisions that would be costly to rediscover.
- Note false turns and why they were rejected.
- Link to relevant commits.
- Keep entries brief — enough to reconstruct reasoning.
- When this file grows too large, archive older entries to
  `.agents/history/` and leave a pointer here.

## Decisions

| Date | Decision | Rationale | Git ref |
| ---- | -------- | --------- | ------- |
| 2026-11-17 | Migrate onto the `copier-uv-plus` template (MODE C, template `2026.11.3`) | One move brings the DOX rail, mise tasks, ruff/ty, Zensical docs, and CI; the `sdo-skills` and `sdo-writer` siblings already run on it | `bf0b1be` |
| 2026-11-17 | Port the CLI from Typer to Cyclopts | The template standardizes on Cyclopts; Typer leaves the dependency set and `typer.testing.CliRunner` has no Cyclopts equivalent, so the CLI tests call `app([...])` directly and expect `SystemExit` | `bf0b1be` |
| 2026-11-17 | Calendar versioning (`YYYY.MM.N` tags) with `uv-dynamic-versioning` | The version comes from the git tag, so releases repeat every month without a manual bump; the static `0.1.0` in `pyproject.toml` is gone | `bf0b1be` |
| 2026-11-17 | Keep `uv.lock` and `.copier-answers.yml` tracked | The lock file makes installs reproducible, and the answers file is what `copier update` reads — the template ignores both, this repo does not | `bf0b1be` |
| 2026-11-17 | Accept one CLI difference: no arguments prints help and exits 0 | Typer's `no_args_is_help` exited 2, Cyclopts exits 0. Command names, option spellings, output formats and the exit code 1 on a catalog error are unchanged | `bf0b1be` |
| 2026-11-17 | Gate the release workflow on `[skip release]` in the last commit message | A local edit of the template's `release.yml`: a `check` job reads the message and the `release` job only runs when it finds no marker, so a commit can veto its own tag and release | `a4f11da` |
| 2026-11-17 | Bump the CI actions to Node 24 majors | The template still pins `jdx/mise-action@v2` and friends, which GitHub now reports as deprecated Node 20 runtimes. The local pins (`mise-action@v5`, `checkout@v7`, `setup-python@v7`, `setup-uv@v10`, `configure-pages@v6`, `upload-pages-artifact@v5`) win over the template, so `copier update` will conflict on the three workflow files | pending |
| 2026-11-17 | Enable GitHub Pages for the docs site | `docs.yml` deploys with the GitHub Actions source, but Pages was never switched on for this repository, so every docs run failed in "Setup Pages". The site is now live at `jr2804.github.io/sdo-skills-mcp` | pending |
| 2026-11-17 | Require Python >= 3.14 and drop 3.13 from the CI matrix | The repo pins CPython 3.14 (commit `af24ca3`); the template's default matrix still tested 3.13, which cannot install the package | `bf0b1be` |
| 2026-11-17 | Correct two false claims in the old root `AGENTS.md` | "shallowest path wins inside a root" is wrong (the first path in sorted path order wins) and "catalog.py stays free of MCP types" is wrong (it uses the FastMCP `Skill` model — only the server import is forbidden) | `bf0b1be` |
