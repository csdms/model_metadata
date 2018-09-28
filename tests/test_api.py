import pytest
import os

from model_metadata.api import query, stage
from model_metadata.errors import (
    MissingValueError,
    MissingSectionError,
    MetadataNotFoundError,
)


def test_query(shared_datadir):
    version = query(str(shared_datadir), "info.version")
    assert version == "10.6"


def test_stage(tmpdir, shared_datadir):
    with tmpdir.as_cwd() as prev:
        manifest = stage(shared_datadir, "./the_stage")
        assert manifest == ["child.in"]

        assert os.listdir("the_stage") == ["child.in"]


def test_stage_with_default_dest(tmpdir, shared_datadir):
    with tmpdir.as_cwd() as prev:
        stage(shared_datadir)
        assert "child.in" in os.listdir(".")


def test_stage_is_filled_out(tmpdir, shared_datadir):
    with tmpdir.as_cwd() as prev:
        stage(shared_datadir, "./the_stage")

        with open("the_stage/child.in", "r") as fp:
            contents = fp.read()
        assert "{{" not in contents
        assert "}}" not in contents


def test_query_with_bad_section(shared_datadir):
    with pytest.raises(MissingSectionError):
        query(shared_datadir, "not-a-section.version")


def test_query_with_bad_value(shared_datadir):
    with pytest.raises(MissingValueError):
        query(shared_datadir, "info.not_a_value")


def test_query_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError):
        with tmpdir.as_cwd():
            query("./not/a/path", "info.version")


def test_stage_with_bad_path(tmpdir):
    with pytest.raises(MetadataNotFoundError):
        with tmpdir.as_cwd():
            stage("./not/a/path", ".")
