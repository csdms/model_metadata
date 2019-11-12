#!/usr/bin/env python
import os
import pathlib
import sys

import pytest
from click.testing import CliRunner

from model_metadata.cli.main import mmd


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(mmd, ["--help"])
    assert result.exit_code == 0

    result = runner.invoke(mmd, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


@pytest.mark.parametrize("subcommand", ("find", "query", "stage"))
def test_subcommand_help(subcommand):
    runner = CliRunner()
    result = runner.invoke(mmd, [subcommand, "--help"])
    assert result.exit_code == 0


def test_stage_subcommand(tmpdir, shared_datadir):
    runner = CliRunner()
    stagedir = pathlib.Path(tmpdir / "stagedir")
    stagedir.mkdir()
    with tmpdir.as_cwd():
        result = runner.invoke(mmd, ["stage", str(shared_datadir), str(stagedir)])
        assert result.exit_code == 0
        manifest = result.stdout.splitlines()
        assert set(stagedir.iterdir()) == set([stagedir / fname for fname in manifest])


def test_stage_subcommand_without_manifest(tmpdir, shared_datadir):
    runner = CliRunner()
    stagedir = pathlib.Path(tmpdir / "stagedir")
    stagedir.mkdir()
    with tmpdir.as_cwd():
        result = runner.invoke(mmd, ["stage", "-q", str(shared_datadir), str(stagedir)])
        assert set(stagedir.iterdir()) == set([stagedir / "child.in"])
        assert result.exit_code == 0
        assert result.stdout == ""


def test_query_subcommand(shared_datadir):
    runner = CliRunner()
    result = runner.invoke(mmd, ["query", str(shared_datadir), "--var", "info.version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "info.version: '10.6'"


def test_query_subcommand_missing_values(shared_datadir):
    runner = CliRunner()
    result = runner.invoke(
        mmd, ["query", str(shared_datadir), "--var", "not_a_section"]
    )
    assert result.exit_code == 1
    result = runner.invoke(
        mmd,
        [
            "query",
            str(shared_datadir),
            "--var=not_a_section",
            "--var=also_not_a_section",
        ],
    )
    assert result.exit_code == 2


@pytest.mark.parametrize("entry_point", ("model:ModelString", "model:ModelPath"))
def test_find(datadir, entry_point):
    runner = CliRunner()
    os.chdir(datadir)
    result = runner.invoke(mmd, ["find", entry_point])
    assert result.exit_code == 0
    assert (pathlib.Path(result.stdout.strip()) / "model.py").is_file()
    # assert result.stdout.strip() == str(datadir)


def test_find_absolute_path(datadir):
    runner = CliRunner()
    os.chdir(datadir)
    result = runner.invoke(mmd, ["find", "model:ModelAbsolutePath"])
    assert result.exit_code == 0
    if sys.platform.startswith("win"):
        assert result.stdout.strip() == "C:\\"
    else:
        assert result.stdout.strip() == "/"
