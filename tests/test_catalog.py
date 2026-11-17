"""Discovery, layer resolution and profile loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from sdo_skills_mcp.catalog import (
    CatalogError,
    available_profiles,
    discover_skills,
    load_layers,
    load_profile,
    resolve,
    select_skills,
)


def test_skills_root_lists_every_skill(skills_root: Path) -> None:
    skills = discover_skills([skills_root])

    assert sorted(skills) == ["etsi-only", "itut-only", "sdo-common"]
    assert skills["sdo-common"].description == "Common drafting skill."
    assert "references/procedures.md" in skills["etsi-only"].files


def test_first_root_wins(tmp_path: Path, skills_root: Path) -> None:
    override = tmp_path / "override"
    override.mkdir()
    (override / "sdo-common").mkdir()
    (override / "sdo-common" / "SKILL.md").write_text("---\nname: sdo-common\ndescription: Override.\n---\n\nWinning body.\n", encoding="utf-8", newline="\n")

    skills = discover_skills([override, skills_root])

    assert skills["sdo-common"].description == "Override."


def test_missing_root_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="skills root does not exist"):
        discover_skills([tmp_path / "nowhere"])


def test_discovery_walks_a_layered_tree(tmp_path: Path) -> None:
    tree = tmp_path / "layered"
    for layer, name, text in (
        ("common", "sdo-common", "Layered common."),
        ("etsi", "etsi-only", "Layered etsi."),
    ):
        (tree / layer / name).mkdir(parents=True)
        (tree / layer / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {text}\n---\n\nBody.\n", encoding="utf-8", newline="\n")
    (tree / "notes").mkdir()

    skills = discover_skills([tree])

    assert sorted(skills) == ["etsi-only", "sdo-common"]
    assert skills["sdo-common"].description == "Layered common."
    assert skills["etsi-only"].description == "Layered etsi."


def test_shallowest_skill_wins_inside_a_root(tmp_path: Path) -> None:
    tree = tmp_path / "skills"
    (tree / "sdo-common").mkdir(parents=True)
    (tree / "sdo-common" / "SKILL.md").write_text("---\nname: sdo-common\ndescription: Top level.\n---\n\nBody.\n", encoding="utf-8", newline="\n")
    nested = tree / "tools" / "sdo-common"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text("---\nname: sdo-common\ndescription: Nested.\n---\n\nBody.\n", encoding="utf-8", newline="\n")

    skills = discover_skills([tree])

    assert skills["sdo-common"].description == "Top level."


def test_invalid_skill_names_the_folder(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    (root / "broken").mkdir(parents=True)
    (root / "broken" / "SKILL.md").write_text("no frontmatter at all\n", encoding="utf-8")

    with pytest.raises(CatalogError, match="broken"):
        discover_skills([root])


def test_load_layers(catalog_file: Path) -> None:
    layers = load_layers(catalog_file)

    assert layers == {"common": ("sdo-common",), "etsi": ("etsi-only",), "itut": ("itut-only",)}


def test_available_profiles(profiles_dir: Path) -> None:
    assert available_profiles(profiles_dir) == ["etsi", "itut"]


def test_load_profile(profiles_dir: Path) -> None:
    profile = load_profile("itut", profiles_dir)

    assert profile.id == "itut"
    assert profile.include == ("common", "itut")


def test_unknown_profile_lists_the_alternatives(profiles_dir: Path) -> None:
    with pytest.raises(CatalogError, match="unknown profile '3gpp' — available: etsi, itut"):
        load_profile("3gpp", profiles_dir)


def test_select_skills_keeps_layer_order(skills_root: Path, catalog_file: Path, profiles_dir: Path) -> None:
    profile = load_profile("etsi", profiles_dir)
    skills = select_skills(discover_skills([skills_root]), load_layers(catalog_file), profile)

    assert [skill.name for skill in skills] == ["sdo-common", "etsi-only"]


def test_select_skills_rejects_unknown_layer(skills_root: Path, catalog_file: Path, profiles_dir: Path) -> None:
    (profiles_dir / "bad.toml").write_text('id = "bad"\ntitle = "Bad"\ndescription = "Bad."\ninclude = ["common", "nope"]\n', encoding="utf-8")
    profile = load_profile("bad", profiles_dir)

    with pytest.raises(CatalogError, match="names unknown layer 'nope' — known: common, etsi, itut"):
        select_skills(discover_skills([skills_root]), load_layers(catalog_file), profile)


def test_select_skills_reports_missing_skills(skills_root: Path, catalog_file: Path, profiles_dir: Path) -> None:
    (catalog_file).write_text('[layers.common]\nskills = ["sdo-common", "gone"]\n\n[layers.etsi]\nskills = ["etsi-only"]\n', encoding="utf-8")
    profile = load_profile("etsi", profiles_dir)

    with pytest.raises(CatalogError, match="needs skills that no root provides: gone"):
        select_skills(discover_skills([skills_root]), load_layers(catalog_file), profile)


def test_resolve_profile_and_skills(skills_root: Path, catalog_file: Path, profiles_dir: Path) -> None:
    profile, skills = resolve("itut", [skills_root], profiles_dir=profiles_dir, catalog_file=catalog_file)

    assert profile.title == "ITU-T Writer"
    assert [skill.name for skill in skills] == ["sdo-common", "itut-only"]
