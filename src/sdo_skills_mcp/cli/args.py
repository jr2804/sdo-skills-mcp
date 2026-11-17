"""CLI arguments, options, and flags for SDO Skills MCP."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

# Environment variable holding the skill roots (os.pathsep-separated).
ROOTS_ENV = "SDO_SKILLS_ROOTS"

# Command-specific arguments

Profile = Annotated[
    str,
    Parameter(help="Writer profile to serve."),
]

Root = Annotated[
    list[Path] | None,
    Parameter(
        name="--root",
        help="Skills root; repeatable, first root wins.",
    ),
]

Transport = Annotated[
    str,
    Parameter(help="Transport: stdio or http."),
]

Host = Annotated[
    str,
    Parameter(help="Bind address for the http transport."),
]

Port = Annotated[
    int,
    Parameter(help="Port for the http transport."),
]
