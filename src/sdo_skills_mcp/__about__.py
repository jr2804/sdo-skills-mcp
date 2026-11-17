"""Version information for SDO Skills MCP."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__title__ = "sdo_skills_mcp"
__description__ = "Serve the SDO writing skills (ETSI, 3GPP, ITU-T) over the Model Context Protocol."
__author__ = "Jan.Reimes"
__email__ = "jan.reimes@head-acoustics.com"
__license__ = "MIT"
__copyright__ = "Copyright 2026, Jan.Reimes"

try:
    __version__ = version("sdo-skills-mcp")
except PackageNotFoundError:  # pragma: no cover - installed packages always have metadata
    __version__ = "0.0.0"  # Fallback for development mode
