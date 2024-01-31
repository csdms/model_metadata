#! /usr/bin/env python
from __future__ import annotations

import contextlib
import sys
import warnings
from collections.abc import Sequence
from typing import Any

import yaml
from model_metadata._utils import setup_yaml_with_canonical_dict


setup_yaml_with_canonical_dict()


def infer_range(
    value: int | float | str, range: tuple[float] | tuple[float, float] | None = None
) -> tuple[float, float] | tuple[int, int] | None:
    """Infer the minimum and maximum limits of a value.

    Parameters
    ----------
    value : int, float, or str
        The value to infer the range of.
    range : tuple, optional
        The specified range for the value.

    Returns
    -------
    tuple or None
        The maximum allowed range for the value.

    Examples
    --------
    >>> from model_metadata.model_parameter import infer_range
    >>> import sys

    >>> infer_range(1.)
    (-inf, inf)
    >>> infer_range(1., range=(0.,))
    (0.0, inf)
    >>> infer_range(1., range=(0., 1.))
    (0.0, 1.0)

    >>> infer_range(1) == (-sys.maxsize, sys.maxsize - 1)
    True
    >>> infer_range(1, range=(0,)) == (0, sys.maxsize - 1)
    True
    >>> infer_range(1, range=(0, 10))
    (0, 10)

    >>> infer_range('lorem ipsum')
    """
    if isinstance(value, float):
        full_range = (float("-inf"), float("inf"))
    elif isinstance(value, int):
        full_range = (-sys.maxsize, sys.maxsize - 1)
    else:
        return None

    if not range:
        return full_range
    elif len(range) == 1:
        return (range[0], full_range[1])
    elif len(range) == 2:
        return (range[0], range[1])
    else:
        raise ValueError(f"range must be or length 1 or 2 ({range!r}")


def range_as_tuple(
    range: tuple[float, float] | None
) -> tuple[None, None] | tuple[float, float]:
    if range is None:
        return (None, None)
    else:
        return (range[0], range[1])


def assert_in_bounds(value: float, bounds: tuple[float | None, float | None]) -> None:
    """Assert that a value is within a certain range.

    Parameters
    ----------
    value : int or float
        Value to test.
    bounds : tuple of int or float
        Lower and upper bound.

    Raises
    ------
    ValueError
        If the value is outside of the bounds.
    """
    try:
        min_val, max_val = bounds
    except (TypeError, ValueError):
        raise ValueError("bounds must be (min, max)")

    if min_val is not None and value < min_val:
        raise ValueError(
            "value is below lower bound ({val} < {bound})".format(
                val=value, bound=min_val
            )
        )
    if max_val is not None and value > max_val:
        raise ValueError(
            "value is above upper bound ({val} > {bound})".format(
                val=value, bound=max_val
            )
        )


def infer_type(value: float | str) -> str:
    inferred: float | str = str(value)
    try:
        inferred = int(inferred)
    except ValueError:
        with contextlib.suppress(ValueError):
            inferred = float(inferred)

    if isinstance(inferred, str):
        if inferred in ("True", "False"):
            return "bool"
        else:
            return "string"
    elif isinstance(inferred, int):
        return "int"
    elif isinstance(inferred, float):
        return "float"
    else:
        raise ValueError("unable to infer data type")


def parameter_from_dict(d: dict[str, Any]) -> ModelParameter:
    kwds: dict[str, Any] = {"desc": d.get("description") or d.get("desc")}

    value = d["value"]
    if isinstance(value, dict):
        # value = d["value"]["default"]
        value = d["value"].pop("default")
        kwds.update(d["value"])
        if "choices" in kwds:
            kwds.setdefault("type", "choice")
        elif "files" in kwds:
            kwds.setdefault("type", "file")
        elif "true_value" in kwds or "false_value" in kwds:
            kwds.setdefault("type", "bool")

    if "range" in kwds and isinstance(kwds["range"], dict):
        kwds["range"] = (kwds["range"]["min"], kwds["range"]["max"])

    # dtype = kwds.get("type") or infer_type(value)
    dtype = kwds.pop("type", None) or infer_type(value)

    if dtype in ("float", "double"):
        return FloatParameter(value, **kwds)
    elif dtype in ("int", "integer", "long"):
        return IntParameter(value, **kwds)
    elif dtype in ("str", "string"):
        return StringParameter(value, **kwds)
    elif dtype in ("choice",):
        return ChoiceParameter(value, **kwds)
    elif dtype in ("file",):
        return FileParameter(value, **kwds)
    elif dtype in ("bool", "boolean"):
        return BooleanParameter(value, **kwds)
    else:
        raise ValueError(f"{dtype}: unknown parameter type")


class ModelParameter:
    _kwds: tuple[str, ...] | tuple[()] = ()
    _dtype: str

    def __init__(self, value: Any, desc: str | None = None, **kwds: dict[str, Any]):
        self._value = value
        self._desc = desc

    @property
    def desc(self) -> str | None:
        return self._desc

    @property
    def value(self) -> Any:
        return self._value

    def as_dict(self) -> dict[str, Any]:
        value = {"default": self.value, "type": self._dtype}
        return {"description": self.desc, "value": value}

    def as_yaml(self) -> str:
        return yaml.safe_dump(self.as_dict(), default_flow_style=False)

    @property
    def type(self) -> str:
        return self._dtype

    def __str__(self) -> str:
        return self.as_yaml()

    def __repr__(self) -> str:
        kwds = ["desc"]
        with contextlib.suppress(AttributeError):
            kwds.extend(self._kwds)
        args = [repr(self.value)] + [f"{arg}={getattr(self, arg)!r}" for arg in kwds]

        return f"{self.__class__.__name__}({', '.join(args)}) "


class StringParameter(ModelParameter):
    _dtype = "str"

    def __init__(self, value: str, desc: str | None = None, **kwds: dict[str, Any]):
        if kwds:
            warnings.warn(
                f"ignoring unrecognized keywords for {self.__class__.__name__}"
                f" ({', '.join(repr(k) for k in kwds)})",
                stacklevel=2,
            )
        super().__init__(str(value), desc=desc)


class NumberParameter(ModelParameter):
    _kwds = ("units", "range")
    _value: int | float

    def __init__(
        self,
        value: float | str,
        desc: str | None = None,
        range: tuple[float, float] | None = None,
        units: str | None = None,
    ):
        range_ = range_as_tuple(range)

        if range_ is not None and len(range_) != 2:
            raise ValueError("range must be either None or (min, max)")

        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                value = float(value)
        if not isinstance(value, (int, float)):
            raise ValueError("value is not a number")

        super().__init__(value, desc=desc)

        self._range = range_
        self._units = units

        assert_in_bounds(self._value, self._range)

    def as_dict(self) -> dict[str, Any]:
        d = super().as_dict()

        value = d["value"]
        if self.units is not None:
            value.update({"units": self.units})

        range_ = {}
        if self.range[0] is not None:
            range_["min"] = self.range[0]
        if self.range[1] is not None:
            range_["max"] = self.range[1]
        if range_:
            value["range"] = range_

        return d

    @property
    def units(self) -> str | None:
        return self._units

    @property
    def range(self) -> tuple[float, float] | tuple[None, None]:
        return self._range


class ChoiceParameter(ModelParameter):
    _dtype = "str"
    _kwds: tuple[str, ...] = ("choices",)
    _choices: tuple[Any, ...]

    def __init__(
        self,
        value: Any,
        desc: str | None = None,
        choices: Sequence[Any] = (),
    ):
        super().__init__(value, desc=desc)

        self._choices = tuple(choice for choice in choices)

        if self.value not in self.choices:
            raise ValueError("value is not contained in choices")

    def as_dict(self) -> dict[str, Any]:
        d = super().as_dict()

        value = d["value"]
        if self.choices:
            value.update({"choices": self.choices})

        return d

    @property
    def choices(self) -> tuple[Any, ...]:
        return self._choices


class BooleanParameter(ChoiceParameter):
    _dtype = "bool"
    _kwds = ("true_value", "false_value")

    def __init__(
        self,
        value: Any,
        desc: str | None = None,
        true_value: Any = True,
        false_value: Any = False,
    ):
        ChoiceParameter.__init__(
            self, value, desc=desc, choices=(true_value, false_value)
        )

    @property
    def true_value(self) -> Any:
        return self._choices[0]

    @property
    def false_value(self) -> Any:
        return self._choices[1]

    @property
    def is_true(self) -> bool:
        return self.value == self.true_value


class FileParameter(ChoiceParameter):
    _dtype = "str"
    _kwds = ("files",)

    def __init__(
        self,
        value: str,
        desc: str | None = None,
        choices: Sequence[str] | None = None,
    ):
        if choices is None:
            choices = (value,)

        super().__init__(value, desc=desc, choices=choices)

    @property
    def files(self) -> tuple[str, ...]:
        return self.choices


class FloatParameter(NumberParameter):
    _dtype = "float"

    def __init__(
        self,
        value: float | str,
        desc: str | None = None,
        range: tuple[float, float] | None = None,
        units: str | None = None,
    ):
        super().__init__(float(value), desc=desc, range=range, units=units)


class IntParameter(NumberParameter):
    _dtype = "int"

    def __init__(
        self,
        value: int | str,
        desc: str | None = None,
        range: tuple[int, int] | None = None,
        units: str | None = None,
    ):
        if isinstance(value, float):
            warnings.warn(
                f"{value}: floating point number passed as an integer parameter, value"
                f" will be truncated to {int(value)}",
                stacklevel=2,
            )
            value = int(value)

        if not isinstance(value, (int, str)):
            raise ValueError(
                "value must be either an int or a string that can be converted to"
                f" an int ({value!r})"
            )
        super().__init__(int(value), desc=desc, range=range, units=units)
