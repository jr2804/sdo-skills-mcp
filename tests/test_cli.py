"""The command line: serve, profiles, catalog, check."""

from __future__ import annotations

import os
import runpy
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from sdo_skills_mcp import cli
from fastmcp import Skill

from sdo_skills_mcp.catalog import Profile, available_profiles, load_layers, load_profile

runner = CliRunner()


def _skill(name: str, description: str) -> Skill:
    return Skill.from_files({"SKILL.md": f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n"})


@pytest.fixture
def served(monkeypatch: pytest.MonkeyPatch) -> Profile:
    """Make the CLI resolve a small in-memory profile."""
    profile = Profile("etsi", "ETSI Writer", "ETSI.", ("common",))
    skills = [_skill("sdo-common", "Common drafting skill.")]
    monkeypatch.setattr(cli, "resolve", lambda profile_id, roots: (profile, skills))
    return profile


def test_profiles_lists_every_profile() -> None:
    result = runner.invoke(cli.app, ["profiles"])

    assert result.exit_code == 0
    assert "ETSI Writer" in result.stdout


def test_packaged_profiles_and_layers_agree() -> None:
    layers = load_layers()
    used: set[str] = set()
    for profile_id in available_profiles():
        include = set(load_profile(profile_id).include)
        assert include <= set(layers), profile_id
        used.update(include)

    assert used == set(layers)


def test_catalog_lists_the_served_skills(served: Profile, tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["catalog", "--root", str(tmp_path)])

    assert result.exit_code == 0
    assert "profile etsi — 1 skills" in result.stdout
    assert "sdo-common" in result.stdout
    assert "Common drafting skill." in result.stdout


def test_serve_reports_a_bad_profile(skills_root: Path) -> None:
    result = runner.invoke(cli.app, ["serve", "--profile", "nope", "--root", str(skills_root)])

    assert result.exit_code == 1
    assert "unknown profile 'nope'" in result.output


def test_catalog_reports_a_bad_profile(skills_root: Path) -> None:
    result = runner.invoke(cli.app, ["catalog", "--profile", "nope", "--root", str(skills_root)])

    assert result.exit_code == 1
    assert "unknown profile 'nope'" in result.output


def test_main_runs_the_app(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["sdo-skills-mcp", "profiles"])

    with pytest.raises(SystemExit) as exit_info:
        cli.main()

    assert exit_info.value.code == 0


def test_module_runs_as_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["sdo-skills-mcp", "profiles"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("sdo_skills_mcp", run_name="__main__")

    assert exit_info.value.code == 0


def test_roots_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(cli.ROOTS_ENV, os.pathsep.join([str(tmp_path / "a"), str(tmp_path / "b")]))

    assert cli.roots_from_env() == [tmp_path / "a", tmp_path / "b"]


def test_roots_fall_back_to_the_current_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(cli.ROOTS_ENV, raising=False)

    assert cli.roots_from_env() == [Path("skills")]


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replace the server with one that records how it was run."""
    recorded: dict[str, Any] = {}

    class Stub:
        def run(self, **kwargs: Any) -> None:
            recorded.update(kwargs)

    monkeypatch.setattr(cli, "build_server", lambda profile, skills: Stub())
    return recorded


def test_serve_runs_the_stdio_transport(served: Profile, stub: dict[str, Any], tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["serve", "--root", str(tmp_path)])

    assert result.exit_code == 0
    assert stub == {"transport": "stdio"}


def test_serve_runs_the_http_transport(served: Profile, stub: dict[str, Any], tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["serve", "--root", str(tmp_path), "--transport", "http", "--port", "9001"])

    assert result.exit_code == 0
    assert stub == {"transport": "http", "host": "127.0.0.1", "port": 9001}


def test_check_names_skills_outside_the_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "load_layers", lambda: {"common": ("sdo-writing",)})
    root = tmp_path / "skills"
    (root / "stray").mkdir(parents=True)
    (root / "stray" / "SKILL.md").write_text("---\nname: stray\ndescription: Stray.\n---\n\nx\n", encoding="utf-8")

    result = runner.invoke(cli.app, ["check", "--root", str(root)])

    assert "stray  (not in catalog.toml)" in result.stdout
    assert "catalog.toml lists skills no root provides: sdo-writing" in result.output


def test_check_reports_a_missing_root(tmp_path: Path) -> None:
    result = runner.invoke(cli.app, ["check", "--root", str(tmp_path / "nowhere")])

    assert result.exit_code == 1
    assert "skills root does not exist" in result.output


def test_check_uses_the_environment_roots(monkeypatch: pytest.MonkeyPatch, skills_root: Path) -> None:
    monkeypatch.setenv(cli.ROOTS_ENV, str(skills_root))
    monkeypatch.setattr(cli, "load_layers", lambda: {})

    result = runner.invoke(cli.app, ["check"])

    assert "3 skills loaded from 1 root(s)" in result.stdout
