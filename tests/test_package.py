"""Smoke tests for the generated package scaffold."""

from __future__ import annotations

import runpy
from importlib.metadata import PackageNotFoundError

import pytest

import sdo_skills_mcp
from sdo_skills_mcp import __about__
from sdo_skills_mcp.cli import app as cli_app


def test_package_exposes_version() -> None:
    """Importing the package and its metadata module must work."""
    assert sdo_skills_mcp.__version__
    assert __about__.__title__ == "sdo_skills_mcp"


def test_cli_version_uses_metadata() -> None:
    """The CLI version callback reads installed package metadata."""
    assert cli_app._get_version()


def test_cli_version_falls_back_without_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI still reports a version when package metadata is unavailable."""

    def missing(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(cli_app, "version", missing)

    assert cli_app._get_version() == "0.0.0"


def test_cli_main_invokes_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """The console entry point delegates to the Cyclopts app."""
    invoked: list[bool] = []
    monkeypatch.setattr(cli_app, "app", lambda: invoked.append(True))

    cli_app.main()

    assert invoked == [True]


def test_dunder_main_invokes_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """`python -m sdo_skills_mcp` runs the CLI entry point."""
    invoked: list[bool] = []
    monkeypatch.setattr(cli_app, "main", lambda: invoked.append(True))

    runpy.run_module("sdo_skills_mcp", run_name="__main__")

    assert invoked == [True]
