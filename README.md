# sdo-skills-mcp

The standards-writing skills of the SDO Writer — ETSI, 3GPP, ITU-T — served over the
[Model Context Protocol](https://modelcontextprotocol.io), so an MCP host can read them
without copying them into every project.

The server exposes the skills through the MCP Skills extension (`skills/list`, `skills/get`,
`skill://<name>/SKILL.md` resources) and, for hosts that do not speak that extension yet,
through two plain tools: `sdo_list_skills` and `sdo_read_skill`.

Skill content is not in this repository. It lives in
[jr2804/sdo-skills](https://github.com/jr2804/sdo-skills); this package decides *which*
skills a profile serves and *how* they reach a host.

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

## Development

```bash
uv sync
uv run pytest          # 100 % coverage gate
uv run sdo-skills-mcp profiles
```

## Layout

```
src/sdo_skills_mcp/
  catalog.toml        # layer -> skill names
  profiles/*.toml     # profile -> layers
  catalog.py          # load, discover, select
  server.py           # FastMCP server, extension + compat tools
  cli.py              # serve, profiles, catalog, check
```
