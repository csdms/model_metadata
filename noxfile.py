from __future__ import annotations

import os
import pathlib

import nox

PROJECT = "model_metadata"
ROOT = pathlib.Path(__file__).parent


@nox.session
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install("-r", "requirements.txt", "-r", "requirements-testing.txt")
    session.install(".", "--no-deps")

    args = ["--cov", PROJECT, "-vvv"] + session.posargs

    if "CI" in os.environ:
        args.append(f"--cov-report=xml:{ROOT.absolute()!s}/coverage.xml")
    session.run("pytest", *args)

    if "CI" not in os.environ:
        session.run("coverage", "report", "--ignore-errors", "--show-missing")


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")
