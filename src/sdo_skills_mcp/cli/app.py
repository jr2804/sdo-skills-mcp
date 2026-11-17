"""Cyclopts CLI app for SDO Skills MCP."""

from __future__ import annotations

from importlib.metadata import version

from cyclopts import App

from sdo_skills_mcp.cli import commands


# Version management
def _get_version() -> str:
    """Get application version from package metadata."""
    try:
        return version("sdo-skills-mcp")
    except Exception:
        return "0.0.0"  # Fallback for development mode


app = App(
    name="sdo-skills-mcp",
    help="Serve the SDO writing skills (ETSI, 3GPP, ITU-T) over the Model Context Protocol.",
    version=_get_version,
    version_flags=["--version", "-v"],
)

# Register commands. Commands are plain functions in commands.py — no
# @app.command decorators there, no import of `app`: this avoids the
# circular import (commands.py <-> app.py) and keeps pyreorder from
# re-sorting this file into a broken state.
app.command(commands.serve)
app.command(commands.profiles)
app.command(commands.catalog)
app.command(commands.check)

# Enable `sdo-skills-mcp --install-completion`.
app.register_install_completion_command()


def main() -> None:
    """Entry point for the CLI application."""
    app()
