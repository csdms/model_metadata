#!/usr/bin/env python
from __future__ import annotations

import contextlib
import os
import pathlib

import pytest
from model_metadata.main import main


def test_cli_version(capsys):
    with contextlib.suppress(SystemExit):
        assert main(["--version"]) == 0
    output = capsys.readouterr().out

    assert "model-metadata" in output


def test_cli_help(capsys):
    with contextlib.suppress(SystemExit):
        assert main(["--help"]) == 0
    output = capsys.readouterr().out

    assert "usage" in output


@pytest.mark.parametrize("subcommand", ("find", "query", "stage"))
def test_subcommand_help(capsys, subcommand):
    with contextlib.suppress(SystemExit):
        assert main([subcommand, "--help"]) == 0


def test_stage_subcommand(capsys, tmpdir, shared_datadir):
    stagedir = pathlib.Path(tmpdir / "stagedir")
    stagedir.mkdir()

    with tmpdir.as_cwd():
        with contextlib.suppress(SystemExit):
            assert main(["stage", "-vvv", str(shared_datadir), str(stagedir)]) == 0
        manifest = capsys.readouterr().out.splitlines()
        assert set(stagedir.iterdir()) == {stagedir / fname for fname in manifest}


def test_query_subcommand(capsys, shared_datadir):
    with contextlib.suppress(SystemExit):
        assert main(["query", "-vvv", "--var=info.version", str(shared_datadir)]) == 0
    assert capsys.readouterr().out.strip() == "info.version: '10.6'"


def test_query_subcommand_missing_values(capsys, shared_datadir):
    with contextlib.suppress(SystemExit):
        assert main(["query", "-vvv", "--var=not-a-section"]) == 1

    with contextlib.suppress(SystemExit):
        assert main(["query", "-vvv", "--var=not-a-section", "--var=foobar"]) == 2


@pytest.mark.parametrize(
    "entry_point", ("testing.model:ModelString", "testing.model:ModelPath")
)
def test_find(capsys, datadir, entry_point):
    with contextlib.suppress(SystemExit):
        assert main(["find", "-vvv", entry_point]) == 0
    assert os.path.isfile(os.path.join(capsys.readouterr().out.strip(), "model.py"))


def test_find_absolute_path(capsys, datadir):
    with contextlib.suppress(SystemExit):
        assert main(["find", "-vvv", "testing.model:ModelAbsolutePath"]) == 0
    actual = pathlib.PurePath(capsys.readouterr().out.strip())
    assert actual.stem == ""
