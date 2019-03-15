from pytest import approx
import pytest
import yaml

from model_metadata.model_parameter import setup_yaml_with_canonical_dict


setup_yaml_with_canonical_dict()


@pytest.mark.parametrize("exponent", ("3",))
@pytest.mark.parametrize("expsign", ("+", ""))
@pytest.mark.parametrize("letter", ("E", "e"))
@pytest.mark.parametrize("coefficient", ("1.0", "1.", "1"))
@pytest.mark.parametrize("sign", ("+", "-", ""))
def test_load_one_thousand(sign, coefficient, letter, expsign, exponent):
    val = yaml.safe_load(sign + coefficient + letter + expsign + exponent)
    if sign == "-":
        val *= -1
    assert val == approx(1000.0)


@pytest.mark.parametrize("exponent", ("3",))
@pytest.mark.parametrize("expsign", ("+", ""))
@pytest.mark.parametrize("letter", ("E", "e"))
@pytest.mark.parametrize("coefficient", (".1", "0.1"))
@pytest.mark.parametrize("sign", ("+", "-", ""))
def test_load_one_hundred(sign, coefficient, letter, expsign, exponent):
    val = yaml.safe_load(sign + coefficient + letter + expsign + exponent)
    if sign == "-":
        val *= -1
    assert val == approx(100.0)


@pytest.mark.parametrize("exponent", ("1",))
@pytest.mark.parametrize("expsign", ("-",))
@pytest.mark.parametrize("letter", ("E", "e"))
@pytest.mark.parametrize("coefficient", ("100.0", "100.", "100"))
@pytest.mark.parametrize("sign", ("+", "-", ""))
def test_load_ten(sign, coefficient, letter, expsign, exponent):
    val = yaml.safe_load(sign + coefficient + letter + expsign + exponent)
    if sign == "-":
        val *= -1
    assert val == approx(10.0)
