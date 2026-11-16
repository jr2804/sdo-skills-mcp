"""Discover the skills on disk and resolve the subset a profile puts in scope."""

from __future__ import annotations

import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from fastmcp import Skill

SKILL_FILE = "SKILL.md"

PACKAGE_DIR = Path(__file__).parent
CATALOG_FILE = PACKAGE_DIR / "catalog.toml"
PROFILES_DIR = PACKAGE_DIR / "profiles"


class CatalogError(Exception):
    """A root, a profile or a layer does not add up."""


@dataclass(frozen=True)
class Profile:
    """One SDO writer profile: the layers it serves, in order."""

    id: str
    title: str
    description: str
    include: tuple[str, ...]


def available_profiles(profiles_dir: Path = PROFILES_DIR) -> list[str]:
    """Return the profile IDs, sorted."""
    return sorted(path.stem for path in profiles_dir.glob("*.toml"))


def load_profile(profile_id: str, profiles_dir: Path = PROFILES_DIR) -> Profile:
    """Read one profile by ID."""
    path = profiles_dir / f"{profile_id}.toml"
    if not path.is_file():
        known = ", ".join(available_profiles(profiles_dir)) or "none"
        raise CatalogError(f"unknown profile {profile_id!r} — available: {known}")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Profile(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        include=tuple(data["include"]),
    )


def load_layers(catalog_file: Path = CATALOG_FILE) -> dict[str, tuple[str, ...]]:
    """Read the layer-to-skill mapping."""
    data = tomllib.loads(catalog_file.read_text(encoding="utf-8"))
    return {layer: tuple(body["skills"]) for layer, body in data["layers"].items()}


def discover_skills(roots: Iterable[Path]) -> dict[str, Skill]:
    """Load every skill under the roots, keyed by name.

    A skill is a directory with a ``SKILL.md``. Roots are read in order and the
    first root that defines a name wins, so a local override can shadow a
    shared checkout.
    """
    skills: dict[str, Skill] = {}
    for root in roots:
        if not root.is_dir():
            raise CatalogError(f"skills root does not exist: {root}")
        for child in sorted(root.iterdir()):
            if not (child / SKILL_FILE).is_file():
                continue
            try:
                skill = Skill.from_directory(child)
            except Exception as exc:  # FastMCP validates the Agent Skills spec
                raise CatalogError(f"{child}: {exc}") from exc
            skills.setdefault(skill.name, skill)
    return skills


def select_skills(
    skills: Mapping[str, Skill],
    layers: Mapping[str, Sequence[str]],
    profile: Profile,
) -> list[Skill]:
    """Return the skills of the profile's layers, in layer order."""
    wanted: list[str] = []
    for layer in profile.include:
        if layer not in layers:
            known = ", ".join(sorted(layers))
            raise CatalogError(f"profile {profile.id!r} names unknown layer {layer!r} — known: {known}")
        wanted.extend(layers[layer])

    missing = sorted({name for name in wanted if name not in skills})
    if missing:
        raise CatalogError(f"profile {profile.id!r} needs skills that no root provides: {', '.join(missing)}")

    return [skills[name] for name in wanted]


def resolve(
    profile_id: str,
    roots: Sequence[Path],
    *,
    profiles_dir: Path = PROFILES_DIR,
    catalog_file: Path = CATALOG_FILE,
) -> tuple[Profile, list[Skill]]:
    """Load a profile and the skills it serves."""
    profile = load_profile(profile_id, profiles_dir)
    skills = select_skills(discover_skills(roots), load_layers(catalog_file), profile)
    return profile, skills
