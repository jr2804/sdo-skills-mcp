"""The FastMCP server: a skills catalog plus a tool pair for hosts without the extension."""

from __future__ import annotations

from collections.abc import Sequence

from fastmcp import FastMCP, Skill
from fastmcp.exceptions import ToolError
from fastmcp.skills.provider import SkillCatalogProvider

from sdo_skills_mcp.catalog import Profile

INSTRUCTIONS = """\
The standards-writing skills of {title}: rules, skeletons, checklists and tooling notes for \
writing standards contributions and deliverables.

Discover them with `skills/list` or by listing the `skill://` resources, and read a whole \
skill with `skills/get` or `read_skill()`. A skill's description says when to use it; load the \
skill that owns the task before you write anything.

Hosts that cannot read resources use the `sdo_list_skills` and `sdo_read_skill` tools instead.
"""


def build_server(profile: Profile, skills: Sequence[Skill]) -> FastMCP:
    """Build the server for one profile."""
    by_name = {skill.name: skill for skill in skills}

    mcp = FastMCP(
        name=f"SDO Skills ({profile.id})",
        instructions=INSTRUCTIONS.format(title=profile.title),
    )
    mcp.add_provider(SkillCatalogProvider(list(skills)))

    @mcp.tool(
        name="sdo_list_skills",
        description=(
            "List the standards-writing skills this server offers, with the description that says "
            "when to use each one. Call this first, then read the skill that owns the task."
        ),
    )
    def sdo_list_skills() -> list[dict[str, str]]:
        return [{"name": skill.name, "description": skill.description} for skill in skills]

    @mcp.tool(
        name="sdo_read_skill",
        description=(
            "Read a standards-writing skill: `path` defaults to SKILL.md, the instructions; "
            "pass a reference path such as `references/procedures.md` to read a supporting file."
        ),
    )
    def sdo_read_skill(name: str, path: str = "SKILL.md") -> str:
        skill = by_name.get(name)
        if skill is None:
            raise ToolError(f"unknown skill {name!r} — call sdo_list_skills for the catalogue")
        content = skill.files.get(path)
        if content is None:
            available = ", ".join(sorted(skill.files))
            raise ToolError(f"{name} has no file {path!r} — available: {available}")
        return _as_text(content)

    return mcp


def _as_text(value: str | bytes) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else value
