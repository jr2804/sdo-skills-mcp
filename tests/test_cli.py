"""The command line: serve, profiles, catalog, check."""

from __future__ import annotations

import os
import runpy
from pathlib import Path
from typing import Any

import pytest
from fastmcp import Skill

from sdo_skills_mcp.catalog import Profile, available_profiles, load_layers, load_profile
from sdo_skills_mcp.cli import app as cli_app
from sdo_skills_mcp.cli import args, commands


def test_profiles_lists_every_profile(capsys: pytest.CaptureFixture[str]) -> None:
    run(["profiles"])

    assert "ETSI Writer" in capsys.readouterr().out


def test_packaged_profiles_and_layers_agree() -> None:
    layers = load_layers()
    used: set[str] = set()
    for profile_id in available_profiles():
        include = set(load_profile(profile_id).include)
        assert include <= set(layers), profile_id
        used.update(include)

    assert used == set(layers)


def test_catalog_lists_the_served_skills(served: Profile, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(["catalog", "--root", str(tmp_path)])

    out = capsys.readouterr().out
    assert "profile etsi — 1 skills" in out
    assert "sdo-common" in out
    assert "Common drafting skill." in out


def test_serve_reports_a_bad_profile(skills_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli_app.app(["serve", "--profile", "nope", "--root", str(skills_root)])

    assert exit_info.value.code == 1
    assert "unknown profile 'nope'" in capsys.readouterr().err


def test_catalog_reports_a_bad_profile(skills_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli_app.app(["catalog", "--profile", "nope", "--root", str(skills_root)])

    assert exit_info.value.code == 1
    assert "unknown profile 'nope'" in capsys.readouterr().err


@pytest.mark.filterwarnings("ignore:Cyclopts application invoked without tokens")
def test_main_runs_the_app(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["sdo-skills-mcp", "profiles"])

    with pytest.raises(SystemExit) as exit_info:
        cli_app.main()

    assert exit_info.value.code == 0
    assert "ETSI Writer" in capsys.readouterr().out


@pytest.mark.filterwarnings("ignore:Cyclopts application invoked without tokens")
def test_module_runs_as_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["sdo-skills-mcp", "profiles"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("sdo_skills_mcp", run_name="__main__")

    assert exit_info.value.code == 0
    assert "ETSI Writer" in capsys.readouterr().out


def test_roots_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(args.ROOTS_ENV, os.pathsep.join([str(tmp_path / "a"), str(tmp_path / "b")]))

    assert commands.roots_from_env() == [tmp_path / "a", tmp_path / "b"]


def test_roots_fall_back_to_the_current_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(args.ROOTS_ENV, raising=False)

    assert commands.roots_from_env() == [Path("skills")]


def test_serve_runs_the_stdio_transport(served: Profile, stub: dict[str, Any], tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(["serve", "--root", str(tmp_path)])

    assert stub == {"transport": "stdio"}
    assert "serving 1 skills for profile etsi over stdio" in capsys.readouterr().err


def test_serve_runs_the_http_transport(served: Profile, stub: dict[str, Any], tmp_path: Path) -> None:
    run(["serve", "--root", str(tmp_path), "--transport", "http", "--port", "9001"])

    assert stub == {"transport": "http", "host": "127.0.0.1", "port": 9001}


@pytest.fixture
def served(monkeypatch: pytest.MonkeyPatch) -> Profile:
    """Make the CLI resolve a small in-memory profile."""
    profile = Profile("etsi", "ETSI Writer", "ETSI.", ("common",))
    skills = [_skill("sdo-common", "Common drafting skill.")]
    monkeypatch.setattr(commands, "resolve", lambda profile_id, roots: (profile, skills))
    return profile


def _skill(name: str, description: str) -> Skill:
    return Skill.from_files({"SKILL.md": f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n"})


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replace the server with one that records how it was run."""
    recorded: dict[str, Any] = {}

    class Stub:
        @staticmethod
        def run(**kwargs: Any) -> None:
            recorded.update(kwargs)

    monkeypatch.setattr(commands, "build_server", lambda profile, skills: Stub())
    return recorded


def test_check_names_skills_outside_the_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(commands, "load_layers", lambda: {"common": ("sdo-writing",)})
    root = tmp_path / "skills"
    (root / "stray").mkdir(parents=True)
    (root / "stray" / "SKILL.md").write_text("---\nname: stray\ndescription: Stray.\n---\n\nx\n", encoding="utf-8")

    run(["check", "--root", str(root)])

    captured = capsys.readouterr()
    assert "stray  (not in catalog.toml)" in captured.out
    assert "catalog.toml lists skills no root provides: sdo-writing" in captured.err


def test_check_reports_a_missing_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli_app.app(["check", "--root", str(tmp_path / "nowhere")])

    assert exit_info.value.code == 1
    assert "skills root does not exist" in capsys.readouterr().err


def test_check_uses_the_environment_roots(monkeypatch: pytest.MonkeyPatch, skills_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv(args.ROOTS_ENV, str(skills_root))
    monkeypatch.setattr(commands, "load_layers", lambda: {})

    run(["check"])

    assert "3 skills loaded from 1 root(s)" in capsys.readouterr().out


def run(tokens: list[str]) -> None:
    """Run the CLI in-process. Cyclopts exits the process when a command returns."""
    with pytest.raises(SystemExit) as exit_info:
        cli_app.app(tokens)

    assert exit_info.value.code == 0
