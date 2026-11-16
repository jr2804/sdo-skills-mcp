"""The MCP surface: the skills extension and the compatibility tools."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.skills import SkillsClientExtension

from sdo_skills_mcp.catalog import Profile, discover_skills, load_layers, load_profile, select_skills
from sdo_skills_mcp.server import _as_text, build_server


@pytest.fixture
def profile(profiles_dir: Path) -> Profile:
    return load_profile("etsi", profiles_dir)


@pytest.fixture
def server(skills_root: Path, catalog_file: Path, profile: Profile) -> FastMCP:
    skills = select_skills(discover_skills([skills_root]), load_layers(catalog_file), profile)
    return build_server(profile, skills)


def test_server_names_the_profile(profile: Profile) -> None:
    server = build_server(profile, [])

    assert server.name == "SDO Skills (etsi)"
    assert profile.title in (server.instructions or "")


async def test_skills_extension_lists_the_profile_only(server: FastMCP) -> None:
    async with Client(server, extensions=[SkillsClientExtension()]) as client:
        skills = await client.list_skills()

    assert sorted(skill.uri for skill in skills) == ["skill://etsi-only/SKILL.md", "skill://sdo-common/SKILL.md"]
    by_uri = {skill.uri: skill for skill in skills}
    assert by_uri["skill://sdo-common/SKILL.md"].frontmatter.description == "Common drafting skill."


async def test_skills_extension_reads_files(server: FastMCP) -> None:
    async with Client(server, extensions=[SkillsClientExtension()]) as client:
        skill = await client.read_skill("skill://etsi-only/SKILL.md")

    assert skill.name == "etsi-only"
    assert "Procedure text." in skill.files["references/procedures.md"].decode("utf-8")


async def test_list_tool_describes_every_skill(server: FastMCP) -> None:
    async with Client(server) as client:
        result = await client.call_tool("sdo_list_skills", {})

    assert result.data == [
        {"name": "sdo-common", "description": "Common drafting skill."},
        {"name": "etsi-only", "description": "ETSI skill."},
    ]


async def test_read_tool_returns_the_instructions_by_default(server: FastMCP) -> None:
    async with Client(server) as client:
        result = await client.call_tool("sdo_read_skill", {"name": "etsi-only"})

    assert "# etsi-only" in result.data
    assert "Body of etsi-only." in result.data


async def test_read_tool_returns_a_reference_file(server: FastMCP) -> None:
    async with Client(server) as client:
        result = await client.call_tool("sdo_read_skill", {"name": "etsi-only", "path": "references/procedures.md"})

    assert result.data == "Procedure text.\n"


async def test_read_tool_rejects_an_unknown_skill(server: FastMCP) -> None:
    async with Client(server) as client:
        with pytest.raises(ToolError, match="unknown skill 'itut-only'"):
            await client.call_tool("sdo_read_skill", {"name": "itut-only"})


async def test_read_tool_rejects_an_unknown_path(server: FastMCP) -> None:
    async with Client(server) as client:
        with pytest.raises(ToolError, match="has no file 'nope.md'"):
            await client.call_tool("sdo_read_skill", {"name": "etsi-only", "path": "nope.md"})


def test_as_text_decodes_bytes() -> None:
    assert _as_text(b"text") == "text"
    assert _as_text("text") == "text"
