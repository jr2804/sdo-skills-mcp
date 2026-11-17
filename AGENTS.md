# sdo-skills-mcp

Serves the SDO writing skills over the Model Context Protocol. Companion to
`sdo-writer` (the agent and installer) and `jr2804/sdo-skills` (the skill content).

## Purpose

Turn "copy 21 skill folders into each project" into "start a server with the right
profile". One MCP server per profile; the host reads skills as resources or through
two compat tools. Content stays in the skills repository — this package only decides
what a profile contains and how it is delivered.

## Ownership

- `src/sdo_skills_mcp/catalog.toml` and `src/sdo_skills_mcp/profiles/*.toml` own the
  profile composition. Editing them changes what every host serves.
- `src/sdo_skills_mcp/catalog.py` owns loading, discovery and selection; it must stay
  free of MCP types so it can be tested without a server.
- `src/sdo_skills_mcp/server.py` owns the FastMCP surface (skills extension + compat tools).
- Skill bodies are **not** owned here. Fix a skill in `jr2804/sdo-skills`, never by
  editing a copy under a root.

## Local contracts

1. **Profiles are data.** A new profile is a TOML file, not a branch in `cli.py`.
2. **First root wins, discovery is recursive.** Layering is by name with the first root
   taking precedence and the shallowest path winning inside a root, so both a flat
   checkout and a layered tree (`skills/<layer>/<skill-id>/`) work;
   `discover_skills` must keep that order stable.
3. **Two delivery paths, one content.** Every skill reachable through the extension is
   also reachable through `sdo_read_skill`; the compat tools are not a reduced mode.
4. **Read-only.** The server never writes, installs or copies skills to disk.
5. **No skill validation of our own.** Frontmatter rules belong to FastMCP's parser;
   we wrap its errors as `CatalogError` and add no second opinion.
6. **The test suite is the contract.** `uv run pytest` gates at 100 % coverage; new
   behaviour comes with a test.
7. **No inline imports.** Imports sit at the top of every module.

## Work guidance

- `uv run sdo-skills-mcp check --root <checkout>` against a real skills checkout is the
  smoke test that matters — it found a YAML defect the fixtures could not.
- `Skill.from_files` keys are relative to the skill root (`SKILL.md`, not `name/SKILL.md`).
- On the client side `Skill.files` values are bytes; the server side uses `_as_text`.
- Windows: write test fixtures with `newline="\n"` or CRLF breaks exact-output asserts.
- `uvx --from <local checkout>` caches the built environment per version: after editing
  the package without bumping the version, `uv cache clean sdo-skills-mcp` (or
  `UV_NO_CACHE=1`) or the run serves the stale build. Git-based installs are rev-keyed
  and never hit this.

## Verification

```bash
uv run pytest                                   # 37 tests, 100 % coverage
uv run sdo-skills-mcp profiles
uv run sdo-skills-mcp check --root <skills> --root <tools>
```

## Child DOX Index

None. One package, one boundary; split only when a folder gains its own contract.
