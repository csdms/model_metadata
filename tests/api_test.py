from __future__ import annotations

import itertools
import os
import pathlib

import pytest
from model_metadata.api import find
from model_metadata.api import query
from model_metadata.api import stage
from model_metadata.errors import MetadataNotFoundError
from model_metadata.errors import MissingSectionError
from model_metadata.errors import MissingValueError
from model_metadata.errors import UnknownKeyError


class Model:
    pass


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_find_from_class(shared_datadir, as_type):
    class Model:
        METADATA = as_type(shared_datadir)

    assert shared_datadir.samefile(find(Model))


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_find_from_instance(shared_datadir, as_type):
    class Model:
        METADATA = as_type(shared_datadir)

    assert shared_datadir.samefile(find(Model()))


@pytest.mark.parametrize("as_type", (str, pathlib.Path))
def test_find_from_path(shared_datadir, as_type):
    path_to_metadata = as_type(shared_datadir)
    assert shared_datadir.samefile(find(path_to_metadata))


def test_find_from_entry_point(shared_datadir):
    Model.METADATA = shared_datadir
    assert shared_datadir.samefile(find(f"{__name__}:Model"))


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


def test_stage_with_default_dest(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        stage(str(shared_datadir))
        assert "child.in" in os.listdir(".")


def test_stage_is_filled_out(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        stage(str(shared_datadir), "./the_stage")

        with open("the_stage/child.in") as fp:
            contents = fp.read()
        assert "{{" not in contents
        assert "}}" not in contents


def test_stage_with_parameters(tmpdir, shared_datadir):
    with tmpdir.as_cwd():
        stage(str(shared_datadir), parameters={"run_duration": 999})

        file_contains_runtime = False
        with open("child.in") as fp:
            for this, next_ in itertools.pairwise(fp):
                file_contains_runtime = this.startswith("RUNTIME")
                if file_contains_runtime:
                    assert next_.startswith("999")
                    break
        assert file_contains_runtime


@pytest.mark.parametrize("params", ({"foo": "bar"}, {"foo": "bar", "baz": "foobar"}))
def test_stage_with_unknown_parameters(tmpdir, shared_datadir, params):
    with tmpdir.as_cwd(), pytest.raises(UnknownKeyError):
        stage(str(shared_datadir), parameters=params)


def test_query_with_bad_section(shared_datadir):
    with pytest.raises(MissingSectionError):
        query(str(shared_datadir), "not-a-section.version")


def test_query_with_bad_value(shared_datadir):
    with pytest.raises(MissingValueError):
        query(str(shared_datadir), "info.not_a_value")


def test_query_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError), tmpdir.as_cwd():
        query("./not/a/path", "info.version")


def test_stage_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError), tmpdir.as_cwd():
        stage("./not/a/path", ".")
