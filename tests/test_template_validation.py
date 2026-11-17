"""Template validation tests for SDO Skills MCP."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_pyproject_toml_structure() -> None:
    """Test that generated pyproject.toml has correct structure."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        msg = "pyproject.toml should exist"
        raise AssertionError(msg)

    with open(pyproject_file, "rb") as f:
        content = tomllib.load(f)

    # Verify required sections
    if "project" not in content:
        msg = "Missing [project] section"
        raise AssertionError(msg)
    if "build-system" not in content:
        msg = "Missing [build-system] section"
        raise AssertionError(msg)
    if "tool" not in content:
        msg = "Missing [tool] section"
        raise AssertionError(msg)

    # Verify project metadata
    if "name" not in content["project"]:
        msg = "Missing project name"
        raise AssertionError(msg)
    if "dynamic" not in content["project"]:
        msg = "Missing 'dynamic' in [project] section (version should be dynamic)"
        raise AssertionError(msg)
    if "version" not in content["project"]["dynamic"]:
        msg = "Missing 'version' in dynamic list"
        raise AssertionError(msg)
    if "description" not in content["project"]:
        msg = "Missing project description"
        raise AssertionError(msg)
    if "requires-python" not in content["project"]:
        msg = "Missing requires-python"
        raise AssertionError(msg)

    # Verify project name matches project slug (kebab-case)
    project_name = content["project"]["name"]
    expected_name = "sdo-skills-mcp"
    if project_name != expected_name:
        msg = f"Project name should be '{expected_name}', got: {project_name}"
        raise AssertionError(msg)


def test_pytest_configuration() -> None:
    """Test that pytest runs coverage with a 100% gate."""
    pyproject_file = Path("pyproject.toml")

    with open(pyproject_file, "rb") as f:
        content = tomllib.load(f)

    tool_section = content.get("tool", {})

    # pytest-cov only reads CLI flags, so they must live in pytest's own addopts.
    pytest_options = tool_section.get("pytest", {}).get("ini_options", {})
    addopts = pytest_options.get("addopts", "")
    expected_slug = "sdo_skills_mcp"
    if f"--cov={expected_slug}" not in addopts:
        msg = f"Coverage should be enabled for '{expected_slug}' via addopts, got: {addopts}"
        raise AssertionError(msg)

    # [tool.pytest-cov] is not a recognised section; make sure it stays gone.
    if "pytest-cov" in tool_section:
        msg = "Stale [tool.pytest-cov] section: pytest-cov does not read it"
        raise AssertionError(msg)

    # The threshold is read by coverage.py itself.
    coverage = tool_section.get("coverage", {})
    if coverage.get("run", {}).get("source") != [expected_slug]:
        msg = f"Coverage source should be ['{expected_slug}']"
        raise AssertionError(msg)
    if coverage.get("report", {}).get("fail_under") != 100:
        msg = "Coverage should require 100%"
        raise AssertionError(msg)


def test_mise_tasks_configured() -> None:
    """Test that mise tasks are configured."""
    mise_file = Path(".config/mise/config.toml")
    if not mise_file.exists():
        msg = ".config/mise/config.toml should exist"
        raise AssertionError(msg)

    # Task definitions live in conf.d/ fragments, not the root config file.
    tasks_file = Path(".config/mise/conf.d/tasks.toml")
    if not tasks_file.exists():
        msg = ".config/mise/conf.d/tasks.toml should exist"
        raise AssertionError(msg)

    # Verify that at least the dev task is present (always included)
    content = tasks_file.read_text(encoding="utf-8")
    if "[tasks.dev]" not in content:
        msg = "Expected [tasks.dev] in conf.d/tasks.toml"
        raise AssertionError(msg)
