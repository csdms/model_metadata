from __future__ import annotations

import os
import pathlib
import shutil

import nox

PROJECT = "model_metadata"
ROOT = pathlib.Path(__file__).parent


@nox.session
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install("-r", "requirements-testing.txt")
    install(session)

    session.run(
        "coverage",
        "run",
        "--branch",
        "--source=model_metadata,tests",
        "--module",
        "pytest",
    )
    session.run("coverage", "report", "--ignore-errors", "--show-missing")
    session.run("coverage", "xml", "-o", "coverage.xml")


@nox.session(name="test-cli")
def test_cli(session: nox.Session) -> None:
    """Test the command line interface."""
    install(session)

    session.run("model-metadata", "--help")
    session.run("model-metadata", "--version")
    session.run("model-metadata", "find", "--help")
    session.run("model-metadata", "query", "--help")
    session.run("model-metadata", "stage", "--help")


@nox.session
def install(session: nox.Session) -> None:
    first_arg = session.posargs[0] if session.posargs else None

    if first_arg:
        if os.path.isfile(first_arg):
            session.install(first_arg)
        else:
            session.error("path must be a source distribution")
    else:
        session.install(".")


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session
def build(session: nox.Session) -> None:
    session.install("pip")
    session.install("build")
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run("python", "-m", "build", "--outdir", "./build/wheelhouse")


@nox.session(name="publish-testpypi")
def publish_testpypi(session):
    """Publish wheelhouse/* to TestPyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(name="publish-pypi")
def publish_pypi(session):
    """Publish wheelhouse/* to PyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory."""
    folders = (
        (ROOT,) if not session.posargs else (pathlib.Path(f) for f in session.posargs)
    )
    for folder in folders:
        if not str(folder.resolve()).startswith(str(ROOT.resolve())):
            session.log(f"skipping {folder}: folder is outside of repository")
            continue

        with session.chdir(folder):
            session.log(f"cleaning {folder}")

            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("dist", ignore_errors=True)
            shutil.rmtree(f"src/{PROJECT}.egg-info", ignore_errors=True)
            shutil.rmtree(".pytest_cache", ignore_errors=True)
            shutil.rmtree(".venv", ignore_errors=True)

            for pattern in ["*.py[co]", "__pycache__"]:
                _clean_rglob(pattern)


def _clean_rglob(pattern):
    nox_dir = pathlib.Path(".nox")

    for p in pathlib.Path(".").rglob(pattern):
        if nox_dir in p.parents:
            continue
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()
