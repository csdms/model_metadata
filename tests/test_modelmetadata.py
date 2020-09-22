import pathlib
import sys

import pytest

from model_metadata import ModelMetadata


class FooBar:

    pass


class BarBaz:

    METADATA = "FooBar"


@pytest.mark.parametrize(
    "model",
    (
        "FooBar",
        "./FooBar",
        pathlib.Path("./FooBar"),
        f"{__name__}:FooBar",
        FooBar,
        FooBar(),
    ),
)
def test_search_paths(model):
    assert ModelMetadata.search_paths(model) == [
        pathlib.Path("FooBar"),
        pathlib.Path(sys.prefix) / "share" / "csdms" / "FooBar",
    ]


@pytest.mark.parametrize("model", (f"{__name__}:BarBaz", BarBaz, BarBaz()))
def test_search_paths_with_metadata(model):
    assert ModelMetadata.search_paths(model) == [
        pathlib.Path(__file__).parent / "FooBar",
        pathlib.Path("BarBaz"),
        pathlib.Path(sys.prefix) / "share" / "csdms" / "BarBaz",
    ]


def test_model_metadata_from_path(shared_datadir):
    meta = ModelMetadata(shared_datadir)
    assert shared_datadir.samefile(meta.base)


def test_model_metadata_from_object(shared_datadir):
    class FooBaz:
        METADATA = shared_datadir

    meta = ModelMetadata.from_obj(FooBaz)
    assert shared_datadir.samefile(meta.base)

    meta = ModelMetadata.from_obj(FooBaz())
    assert shared_datadir.samefile(meta.base)
