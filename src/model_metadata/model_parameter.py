#! /usr/bin/env python
import re
import sys
from collections import OrderedDict

import yaml


def setup_yaml_with_canonical_dict():
    """ https://stackoverflow.com/a/8661021 """
    yaml.add_representer(
        OrderedDict,
        lambda self, data: self.represent_mapping(
            "tag:yaml.org,2002:map", data.items()
        ),
        Dumper=yaml.SafeDumper,
    )

    def repr_ordered_dict(self, data):
        return self.represent_mapping("tag:yaml.org,2002:map", data.items())

    yaml.add_representer(dict, repr_ordered_dict, Dumper=yaml.SafeDumper)

    def repr_dict(self, data):
        return self.represent_mapping(
            "tag:yaml.org,2002:map", sorted(data.items(), key=lambda t: t[0])
        )

    yaml.add_representer(dict, repr_dict, Dumper=yaml.SafeDumper)

    # https://stackoverflow.com/a/45004464
    def repr_str(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_str(data)

    yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

    def repr_tuple(dumper, data):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data))

    yaml.add_representer(tuple, repr_tuple, Dumper=yaml.SafeDumper)

    yaml.add_implicit_resolver(
        u"tag:yaml.org,2002:float",
        re.compile(
            r"""^(?:
         [-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |[-+]?\.[0-9_]+(?:[eE][-+]?[0-9]+)
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*
        |[-+]?\.(?:inf|Inf|INF)
        |\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
        Loader=yaml.SafeLoader,
    )


setup_yaml_with_canonical_dict()


def infer_range(value, range=None):
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
    if isinstance(value, int):
        full_range = (-sys.maxsize, sys.maxsize - 1)
    elif isinstance(value, float):
        full_range = (float("-inf"), float("inf"))
    else:
        return None

    if not range:
        return full_range
    elif len(range) == 1:
        return (range[0], full_range[1])
    elif len(range) == 2:
        return (range[0], range[1])


def range_as_tuple(range):
    if range is None:
        min_max = (None, None)
    else:
        min_max = (range[0], range[1])
    return min_max


def assert_in_bounds(value, bounds):
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


def infer_type(value):
    inferred = str(value)
    try:
        inferred = int(inferred)
    except ValueError:
        try:
            inferred = float(inferred)
        except ValueError:
            pass

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


def parameter_from_dict(d):
    kwds = dict(desc=d.get("description", None) or d.get("desc", None))

    value = d["value"]
    if isinstance(value, dict):
        value = d["value"]["default"]
        kwds.update(d["value"])
        if "choices" in kwds:
            kwds.setdefault("type", "choice")
        elif "files" in kwds:
            kwds.setdefault("type", "file")
        elif "true_value" in kwds or "false_value" in kwds:
            kwds.setdefault("type", "bool")

    if "range" in kwds and isinstance(kwds["range"], dict):
        kwds["range"] = (kwds["range"]["min"], kwds["range"]["max"])

    dtype = kwds.get("type", None) or infer_type(value)

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
        raise ValueError("{dtype}: unknown parameter type".format(dtype=dtype))


class ModelParameterMixIn(object):
    def as_dict(self):
        d = {
            "description": self.desc,
            "value": {"default": self.value, "type": self._dtype},
        }
        try:
            kwds = self._kwds
        except AttributeError:
            kwds = []
        for attr in kwds:
            d["value"][attr] = getattr(self, attr)
        return d

    def as_yaml(self):
        return yaml.safe_dump(self.as_dict(), default_flow_style=False)

    @property
    def type(self):
        return self._dtype

    def __str__(self):
        return self.as_yaml()

    def __repr__(self):
        args = [repr(self.value)]
        kwds = ["desc"]
        try:
            kwds.extend(self._kwds)
        except AttributeError:
            pass
        else:
            for arg in kwds:
                args.append("{k}={v}".format(k=arg, v=repr(getattr(self, arg))))
        return "{cls}({args})".format(cls=self.__class__.__name__, args=", ".join(args))


class StringParameter(ModelParameterMixIn):

    _dtype = "str"

    def __init__(self, value, **kwds):
        self._value = str(value)
        self._desc = kwds.get("desc", None)

    @property
    def desc(self):
        return self._desc

    @property
    def value(self):
        return self._value


class NumberParameter(StringParameter, ModelParameterMixIn):

    _kwds = ("units", "range")

    def __init__(self, value, **kwds):
        range = range_as_tuple(kwds.get("range", None))
        units = kwds.get("units", None)

        if range is not None and len(range) != 2:
            raise ValueError("range must be either None or (min, max)")

        StringParameter.__init__(self, value, **kwds)

        try:
            self._value = int(self._value)
        except ValueError:
            self._value = float(self._value)
        finally:
            if not isinstance(self._value, (int, float)):
                raise ValueError("value is not a number")

        self._range = range
        self._units = units

        assert_in_bounds(self._value, self._range)

    @property
    def units(self):
        return self._units

    @property
    def range(self):
        return self._range


class ChoiceParameter(StringParameter, ModelParameterMixIn):

    _dtype = "str"
    _kwds = ("choices",)

    def __init__(self, value, **kwds):
        choices = kwds.get("choices", [])

        StringParameter.__init__(self, value, **kwds)

        self._choices = tuple([str(choice) for choice in choices])

        if self.value not in self.choices:
            raise ValueError("default is not contained in valid choices")

    @property
    def choices(self):
        return self._choices


class BooleanParameter(ChoiceParameter, ModelParameterMixIn):

    _dtype = "bool"
    _kwds = ("true_value", "false_value")

    def __init__(self, value, **kwds):
        kwds.setdefault(
            "choices", [kwds.get("true_value", True), kwds.get("false_value", False)]
        )

        ChoiceParameter.__init__(self, value, **kwds)

    @property
    def true_value(self):
        return self._choices[0]

    @property
    def false_value(self):
        return self._choices[1]

    @property
    def is_true(self):
        return self.value == self.true_value


class FileParameter(ChoiceParameter, ModelParameterMixIn):

    _dtype = "str"
    _kwds = ("files",)

    def __init__(self, value, **kwds):
        kwds["choices"] = kwds.get("files", (value,))

        ChoiceParameter.__init__(self, value, **kwds)

    @property
    def files(self):
        return self.choices


class FloatParameter(NumberParameter, ModelParameterMixIn):

    _dtype = "float"

    def __init__(self, value, **kwds):
        NumberParameter.__init__(self, value, **kwds)

        self._value = float(self._value)


class IntParameter(NumberParameter, ModelParameterMixIn):

    _dtype = "int"

    def __init__(self, value, **kwds):
        NumberParameter.__init__(self, value, **kwds)

        self._value = int(self._value)


class ModelParameter(object):

    """An input parameter for a model."""

    def __init__(self, value, desc=None, units=None, range=None, dtype=None):
        if dtype:
            self._value = dtype(value)
        else:
            self._value = value
        self._dtype = type(self._value)

        self._desc = desc

        self._range = infer_range(self._value, range=range)
        self._units = units

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def units(self):
        return self._units

    @property
    def desc(self):
        return self._desc

    @property
    def dtype(self):
        return self._dtype

    @property
    def dtype_str(self):
        if self.dtype is int:
            return "int"
        elif self.dtype is float:
            return "float"
        elif self.dtype is str:
            return "str"
        else:
            return self.dtype

    @property
    def type(self):
        return self._dtype

    @property
    def range(self):
        return self._range

    @property
    def choices(self):
        return self._choices

    @staticmethod
    def norm(param):
        desc = param.get("description", None) or param.get("desc", None)

        value = param["value"]
        if isinstance(value, dict):
            value = param["value"]["default"]
            attrs = param["value"]

        units = attrs.get("units", None)
        range = attrs.get("range", None)
        dtype = attrs.get("type", None)

        if dtype == "int":
            dtype = int
        elif dtype == "float":
            dtype = float
        elif dtype in ("str", "string", "file", "choice"):
            dtype = str

        if isinstance(range, dict):
            range = (range["min"], range["max"])

        return ModelParameter(
            value, desc=desc, units=units, range=range, dtype=dtype
        ).as_dict()

    def as_dict(self):
        range = self.range
        if range:
            range = dict(min=self.dtype(range[0]), max=self.dtype(range[1]))

        d = {
            "description": self.desc,
            "value": {
                "default": self.value,
                "type": self.dtype_str,
                "units": self.units,
                "range": range,
            },
        }
        return d

    def as_yaml(self):
        return yaml.dump(self.as_dict(), default_flow_style=False)

    def __str__(self):
        return self.as_yaml()

    def __repr__(self):
        args = [repr(self.value)]
        for arg in self._kwds:
            args.append("{k}={v}".format(k=arg, v=repr(getattr(self, arg))))
        return "{cls}({args})".format(cls=self.__class__, args=", ".join(args))
