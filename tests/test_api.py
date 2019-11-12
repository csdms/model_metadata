import os
import pathlib

import pytest

from model_metadata.api import find, query, stage, install
from model_metadata.errors import (
    MissingValueError,
    MissingSectionError,
    MetadataNotFoundError,
)


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_find_from_object(shared_datadir, as_type):
    class Model:
        METADATA = as_type(shared_datadir)
    assert shared_datadir.samefile(find(Model))


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_find_from_path(shared_datadir, as_type):
    path_to_metadata = as_type(shared_datadir)
    assert shared_datadir.samefile(find(path_to_metadata))


def test_find_bad_model_raises_not_found_error(shared_datadir):
    with pytest.raises(MetadataNotFoundError):
        find("/path/does/not/exist")

    assert (shared_datadir / "child.in").is_file()
    with pytest.raises(MetadataNotFoundError):
        find(shared_datadir / "child.in")


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_query(shared_datadir, as_type):
    version = query(as_type(shared_datadir), "info.version")
    assert version == "10.6"


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
@pytest.mark.parametrize(
    "dest",
    ("the_stage", pathlib.Path("the_stage")),
)
def test_stage(tmpdir, shared_datadir, as_type, dest):
    with tmpdir.as_cwd():
        manifest = stage(as_type(shared_datadir), dest)
        assert set(manifest) == set(os.listdir(dest))


def test_install(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        install(str(shared_datadir), "./dest")
        installed_files = os.listdir("./dest")
        installed_files.sort()
        assert installed_files == [
            "api.yaml",
            "child.in",
            "info.yaml",
            "parameters.yaml",
            "run.yaml",
        ]
        for fname in installed_files:
            assert os.path.isfile(os.path.join("dest", fname))
            assert not os.path.islink(os.path.join("dest", fname))


def test_install_develop(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        install(str(shared_datadir), "./dest", develop=True)
        installed_files = os.listdir("./dest")
        installed_files.sort()
        assert installed_files == [
            "api.yaml",
            "child.in",
            "info.yaml",
            "parameters.yaml",
            "run.yaml",
        ]
        for fname in installed_files:
            assert os.path.islink(os.path.join("dest", fname))


def test_install_clobber(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        os.mkdir("./dest")
        with open(os.path.join("dest", "child.in"), "w") as fp:
            fp.write("")
        with pytest.raises(OSError):
            install(str(shared_datadir), "./dest", clobber=False)
        install(str(shared_datadir), "./dest", clobber=True)


def test_stage_with_default_dest(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        stage(str(shared_datadir))
        assert "child.in" in os.listdir(".")


def test_stage_is_filled_out(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        stage(str(shared_datadir), "./the_stage")

        with open("the_stage/child.in", "r") as fp:
            contents = fp.read()
        assert "{{" not in contents
        assert "}}" not in contents


def test_query_with_bad_section(shared_datadir):
    with pytest.raises(MissingSectionError):
        query(str(shared_datadir), "not-a-section.version")


def test_query_with_bad_value(shared_datadir):
    with pytest.raises(MissingValueError):
        query(str(shared_datadir), "info.not_a_value")


def test_query_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError):
        with tmpdir.as_cwd():
            query("./not/a/path", "info.version")


def test_stage_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError):
        with tmpdir.as_cwd():
            stage("./not/a/path", ".")
