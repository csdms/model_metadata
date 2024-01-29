from __future__ import annotations

import pytest


@pytest.fixture
def model_as_object():
    class Model:
        METADATA = "path"
