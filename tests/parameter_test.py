from __future__ import annotations

import pytest
from model_metadata.model_parameter import FloatParameter
from model_metadata.model_parameter import IntParameter


@pytest.mark.parametrize("value", (1973, 1973.0, 1973.5, "1973"))
def test_int_parameter(value):
    p = IntParameter(value)
    assert isinstance(p.value, int)
    assert p.value == 1973


@pytest.mark.parametrize("value", (3.14, "3.14"))
def test_float_parameter(value):
    p = FloatParameter(value)
    assert isinstance(p.value, float)
    assert p.value == 3.14
