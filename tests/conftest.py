"""Fixtures: a throwaway skills tree, a catalog and a set of profiles."""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_TEXT = """\
---
name: {name}
description: {description}
---

# {name}

Body of {name}.
"""


def write_skill(root: Path, name: str, description: str = "A test skill.", *, extra: dict[str, str] | None = None) -> Path:
    """Write one skill directory and return it."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(SKILL_TEXT.format(name=name, description=description), encoding="utf-8", newline="\n")
    for relative, text in (extra or {}).items():
        target = skill_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    return skill_dir


@pytest.fixture
def skills_root(tmp_path: Path) -> Path:
    """A root with three skills, one of them carrying a reference file."""
    root = tmp_path / "skills"
    root.mkdir()
    write_skill(root, "sdo-common", "Common drafting skill.")
    write_skill(root, "etsi-only", "ETSI skill.", extra={"references/procedures.md": "Procedure text.\n"})
    write_skill(root, "itut-only", "ITU-T skill.")
    (root / "not-a-skill").mkdir()
    (root / "not-a-skill" / "README.md").write_text("no SKILL.md here\n", encoding="utf-8")
    return root


@pytest.fixture
def catalog_file(tmp_path: Path) -> Path:
    """A layer map over the fixture skills."""
    path = tmp_path / "catalog.toml"
    path.write_text(
        '[layers.common]\nskills = ["sdo-common"]\n\n'
        '[layers.etsi]\nskills = ["etsi-only"]\n\n'
        '[layers.itut]\nskills = ["itut-only"]\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture
def profiles_dir(tmp_path: Path) -> Path:
    """Two profiles over the fixture layers."""
    path = tmp_path / "profiles"
    path.mkdir()
    (path / "etsi.toml").write_text(
        'id = "etsi"\ntitle = "ETSI Writer"\ndescription = "ETSI."\ninclude = ["common", "etsi"]\n',
        encoding="utf-8",
    )
    (path / "itut.toml").write_text(
        'id = "itut"\ntitle = "ITU-T Writer"\ndescription = "ITU-T."\ninclude = ["common", "itut"]\n',
        encoding="utf-8",
    )
    return path
