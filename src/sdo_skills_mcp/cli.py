"""Command line: serve a profile, list the profiles, check a skills root."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from sdo_skills_mcp.catalog import (
    CatalogError,
    available_profiles,
    discover_skills,
    load_layers,
    load_profile,
    resolve,
)
from sdo_skills_mcp.server import build_server

ROOTS_ENV = "SDO_SKILLS_ROOTS"

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Serve the SDO writing skills (ETSI, 3GPP, ITU-T) over the Model Context Protocol.",
)


def roots_from_env() -> list[Path]:
    """Roots from ``SDO_SKILLS_ROOTS`` (os.pathsep-separated), else ``./skills``."""
    raw = os.environ.get(ROOTS_ENV, "")
    parts = [part for part in raw.split(os.pathsep) if part]
    return [Path(part) for part in parts] or [Path("skills")]


def _fail(exc: CatalogError) -> typer.Exit:
    typer.echo(f"error: {exc}", err=True)
    return typer.Exit(code=1)


@app.command()
def serve(
    profile: Annotated[str, typer.Option(help="Writer profile to serve.")] = "etsi",
    root: Annotated[list[Path] | None, typer.Option("--root", help="Skills root; repeatable, first root wins.")] = None,
    transport: Annotated[str, typer.Option(help="Transport: stdio or http.")] = "stdio",
    host: Annotated[str, typer.Option(help="Bind address for the http transport.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port for the http transport.")] = 8000,
) -> None:
    """Serve one writer profile over MCP."""
    try:
        profile_model, skills = resolve(profile, list(root) if root else roots_from_env())
    except CatalogError as exc:
        raise _fail(exc) from exc

    mcp = build_server(profile_model, skills)
    typer.echo(f"serving {len(skills)} skills for profile {profile_model.id} over {transport}", err=True)
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="http", host=host, port=port)


@app.command()
def profiles() -> None:
    """List the writer profiles."""
    for profile_id in available_profiles():
        profile = load_profile(profile_id)
        typer.echo(f"{profile.id:8} {profile.title:16} {profile.description}")


@app.command()
def catalog(
    profile: Annotated[str, typer.Option(help="Writer profile to list.")] = "etsi",
    root: Annotated[list[Path] | None, typer.Option("--root", help="Skills root; repeatable, first root wins.")] = None,
) -> None:
    """List the skills a profile serves, in order."""
    try:
        profile_model, skills = resolve(profile, list(root) if root else roots_from_env())
    except CatalogError as exc:
        raise _fail(exc) from exc

    typer.echo(f"profile {profile_model.id} — {len(skills)} skills")
    for skill in skills:
        typer.echo(f"  {skill.name:32} {skill.description.splitlines()[0][:96]}")


@app.command()
def check(
    root: Annotated[list[Path] | None, typer.Option("--root", help="Skills root; repeatable, first root wins.")] = None,
) -> None:
    """Validate every skill under the roots and report what the layers expect."""
    try:
        skills = discover_skills(list(root) if root else roots_from_env())
    except CatalogError as exc:
        raise _fail(exc) from exc

    layers = load_layers()
    known = {name for names in layers.values() for name in names}
    typer.echo(f"{len(skills)} skills loaded from {len(list(root) if root else roots_from_env())} root(s)")
    for name in sorted(skills):
        marker = "" if name in known else "  (not in catalog.toml)"
        typer.echo(f"  {name}{marker}")
    unknown = sorted(known - set(skills))
    if unknown:
        typer.echo(f"catalog.toml lists skills no root provides: {', '.join(unknown)}", err=True)


def main() -> None:
    """Console entry point."""
    app()
