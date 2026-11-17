"""CLI command implementations for SDO Skills MCP."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sdo_skills_mcp.catalog import (
    CatalogError,
    available_profiles,
    discover_skills,
    load_layers,
    load_profile,
    resolve,
)
from sdo_skills_mcp.cli import args
from sdo_skills_mcp.server import build_server


def serve(
    *,
    profile: args.Profile = "etsi",
    root: args.Root = None,
    transport: args.Transport = "stdio",
    host: args.Host = "127.0.0.1",
    port: args.Port = 8000,
) -> None:
    """Serve one writer profile over MCP."""
    try:
        profile_model, skills = resolve(profile, _roots(root))
    except CatalogError as exc:
        raise _fail(exc) from exc

    mcp = build_server(profile_model, skills)
    print(f"serving {len(skills)} skills for profile {profile_model.id} over {transport}", file=sys.stderr)
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="http", host=host, port=port)


def profiles() -> None:
    """List the writer profiles."""
    for profile_id in available_profiles():
        profile = load_profile(profile_id)
        print(f"{profile.id:8} {profile.title:16} {profile.description}")


def catalog(
    *,
    profile: args.Profile = "etsi",
    root: args.Root = None,
) -> None:
    """List the skills a profile serves, in order."""
    try:
        profile_model, skills = resolve(profile, _roots(root))
    except CatalogError as exc:
        raise _fail(exc) from exc

    print(f"profile {profile_model.id} — {len(skills)} skills")
    for skill in skills:
        print(f"  {skill.name:32} {skill.description.splitlines()[0][:96]}")


def check(
    *,
    root: args.Root = None,
) -> None:
    """Validate every skill under the roots and report what the layers expect."""
    roots = _roots(root)
    try:
        skills = discover_skills(roots)
    except CatalogError as exc:
        raise _fail(exc) from exc

    layers = load_layers()
    known = {name for names in layers.values() for name in names}
    print(f"{len(skills)} skills loaded from {len(roots)} root(s)")
    for name in sorted(skills):
        marker = "" if name in known else "  (not in catalog.toml)"
        print(f"  {name}{marker}")
    unknown = sorted(known - set(skills))
    if unknown:
        print(f"catalog.toml lists skills no root provides: {', '.join(unknown)}", file=sys.stderr)


def _roots(root: list[Path] | None) -> list[Path]:
    """The roots given on the command line, else the roots from the environment."""
    return list(root) if root else roots_from_env()


def roots_from_env() -> list[Path]:
    """Roots from ``SDO_SKILLS_ROOTS`` (os.pathsep-separated), else ``./skills``."""
    raw = os.environ.get(args.ROOTS_ENV, "")
    parts = [part for part in raw.split(os.pathsep) if part]
    return [Path(part) for part in parts] or [Path("skills")]


def _fail(exc: CatalogError) -> SystemExit:
    """Report a catalog error on stderr and exit with code 1."""
    print(f"error: {exc}", file=sys.stderr)
    return SystemExit(1)
