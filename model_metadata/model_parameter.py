#! /usr/bin/env python
import os
import sys
from collections import OrderedDict

try:
    import yaml
except ImportError:
    pass


def setup_yaml_with_canonical_dict():
    """ https://stackoverflow.com/a/8661021 """
    yaml.add_representer(
        OrderedDict,
        lambda self, data:  self.represent_mapping('tag:yaml.org,2002:map',
                                                   data.items()),
        Dumper=yaml.SafeDumper)

    def repr_ordered_dict(self, data):
        return self.represent_mapping(
            'tag:yaml.org,2002:map', data.items())

    yaml.add_representer(dict, repr_ordered_dict, Dumper=yaml.SafeDumper)

    def repr_dict(self, data):
        return self.represent_mapping(
            'tag:yaml.org,2002:map',
            sorted(data.items(), key=lambda t: t[0]))

    # yaml.add_representer(
    #     dict,
    #     lambda self, data:  self.represent_mapping(
    #         'tag:yaml.org,2002:map',
    #         sorted(data.items(), key=lambda t: t[0])),
    #     Dumper=yaml.SafeDumper)
    # yaml.add_representer(
    #     dict,
    #     repr_dict,
    #     Dumper=yaml.SafeDumper)
    yaml.add_representer(dict, repr_dict, Dumper=yaml.SafeDumper)

    # https://stackoverflow.com/a/45004464
    def repr_str(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar(
                'tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_str(data)

    yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)


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
    >>> from model_metadata import infer_range

    >>> infer_range(1.)
    (-inf, inf)
    >>> infer_range(1., range=(0.,))
    (0., inf)
    >>> infer_range(1., range=(0., 1.))
    (0., 1.)

    >>> infer_range(1)
    (-inf, inf)
    >>> infer_range(1, range=(0,))
    (0, inf)
    >>> infer_range(1, range=(0, 10))
    (0, 10)

    >>> infer_range('lorem ipsum')
    """
    if isinstance(value, int):
        full_range = (-sys.maxsize, -sys.maxsize - 1)
    elif isinstance(value, float):
        full_range = (float('-inf'), float('inf'))
    else:
        return None

    if not range:
        return full_range
    elif len(range) == 1:
        return (range[0], full_range[1])
    elif len(range) == 2:
        return (range[0], range[1])


def infer_type(value):
    inferred = str(value)
    try:
        inferred = int(inferred)
    except ValueError:
        inferred = float(inferred)

    if isinstance(inferred, str):
        return 'string'
    elif isinstance(inferred, int):
        return 'int'
    elif isinstance(inferred, float):
        return 'float'


def parameter_from_dict(d):
    kwds = dict(desc=d.get('description', None) or d.get('desc', None))

    value = d['value']
    if isinstance(value, dict):
        value = d['value']['default']
        kwds.update(d['value'])
    else:
        kwds.update(d)

    if 'range' in kwds and isinstance(kwds['range'], dict):
        kwds['range'] = (kwds['range']['min'], kwds['range']['max'])

    dtype = kwds.get('type', None) or infer_type(value)

    if dtype in ('float', 'double'):
        return FloatParameter(value, **kwds)
    elif dtype in ('int', 'integer'):
        return IntParameter(value, **kwds)
    elif dtype in ('str', 'string'):
        return StringParameter(value, **kwds)
    elif dtype in ('choice', ):
        return ChoiceParameter(value, **kwds)
    elif dtype in ('file', ):
        return FileParameter(value, **kwds)
    else:
        raise ValueError('{dtype}: unknown parameter type'.format(dtype=dtype))


class StringParameter(object):

    _dtype = 'str'

    # def __init__(self, value, desc=None):
    def __init__(self, value, **kwds):
        self._value = str(value)
        self._desc = kwds.get('desc', None)

    @property
    def desc(self):
        return self._desc

    @property
    def value(self):
        return self._value

    def as_dict(self):
        return {
            'description': self.desc,
            'value': {
                'default': self._value,
                'type': self._dtype,
            },
        }


class NumberParameter(StringParameter):

    # def __init__(self, value, desc=None, units=None, range=None):
    def __init__(self, value, **kwds):
        range = kwds.get('range', None)
        units = kwds.get('units', None)

        StringParameter.__init__(self, value, **kwds)

        try:
            self._value = int(self._value)
        except ValueError:
            self._value = float(self._value)
        finally:
            if not isinstance(self._value, (int, float)):
                raise ValueError('value is not a number')

        self._range = infer_range(self._value, range=range)
        self._units = units

        if self.value < self.range[0] or self.value > self.range[1]:
            raise ValueError('default value is outside specified range')

    @property
    def units(self):
        return self._units

    @property
    def range(self):
        return self._range

    def as_dict(self):
        d = StringParameter.as_dict(self)
        d['value']['range'] = {
            'min': self.range[0],
            'max': self.range[1],
        }
        d['value']['units'] = self.units
        return d


class ChoiceParameter(StringParameter):

    _dtype = 'choice'

    # def __init__(self, value, desc=None, choices=None, dtype=None):
    def __init__(self, value, **kwds):
        choices = kwds.get('choices', [])

        StringParameter.__init__(self, value, **kwds)

        self._choices = tuple([str(choice) for choice in choices])

        if self.value not in self.choices:
            raise ValueError('default is not contained in valid choices')

    @property
    def choices(self):
        return self._choices

    def as_dict(self):
        d = StringParameter.as_dict(self)
        d['value']['choices'] = self.choices
        return d


class FileParameter(StringParameter):

    _dtype = 'file'

    # def __init__(self, value, desc=None, files=None):
    def __init__(self, value, **kwds):
        self._files = kwds.get('files', ())

        StringParameter.__init__(self, value, **kwds)

        if self.value not in self.files:
            raise ValueError('default file is not contained in valid files')

    @property
    def files(self):
        return self._files

    def as_dict(self):
        d = StringParameter.as_dict(self)
        d['value']['files'] = self.files
        return d


class FloatParameter(NumberParameter):

    _dtype = 'float'

    # def __init__(self, value, desc=None, units=None, range=None):
    def __init__(self, value, **kwds):
        NumberParameter.__init__(self, value, **kwds)

        self._value = float(self._value)


class IntParameter(NumberParameter):

    _dtype = 'int'

    # def __init__(self, value, desc=None, units=None, range=None):
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
            return 'int'
        elif self.dtype is float:
            return 'float'
        elif self.dtype is str:
            return 'str'
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

    @classmethod
    def from_yaml(cls, stream):
        """Load a parameter from a yaml-formatted string.

        Parameters
        ----------
        stream : str or file_like
            YAML-formatted text.

        Returns
        -------
        ModelInputParameter
            A new instance of a model parameter.

        Examples
        --------
        >>> from model_metadata import ModelParameter
        >>> buffer = '''
        ... dt:
        ...   desc: Time step.
        ...   value: 1.
        ... '''
        >>> ModelParameter.from_yaml("dt: )
        """
        import yaml

        kwds = yaml.load(buffer)
        name = kwds.keys[0]

        return cls(name, **kwds[name])

    @staticmethod
    def norm(param):
        desc = param.get('description', None) or param.get('desc', None)

        value = param['value']
        if isinstance(value, dict):
            value = param['value']['default']
            attrs = param['value']

        units = attrs.get('units', None)
        range = attrs.get('range', None)
        dtype = attrs.get('type', None)

        if dtype == 'int':
            dtype = int
        elif dtype == 'float':
            dtype = float
        elif dtype in ('str', 'string', 'file', 'choice'):
            dtype = str

        if isinstance(range, dict):
            range = (range['min'], range['max'])

        return ModelParameter(value, desc=desc, units=units, range=range,
                              dtype=dtype).as_dict()

    def as_dict(self):
        range = self.range
        if range:
            range = dict(min=self.dtype(range[0]),
                         max=self.dtype(range[1]))

        d = {
            'description': self.desc,
            'value': {
                'default': self.value,
                'type': self.dtype_str,
                'units': self.units,
                'range': range,
            }
        }
        return d

    def as_yaml(self):
        return yaml.dump(self.as_dict(), default_flow_style=False)

    def __str__(self):
        return self.as_yaml()

    def __repr__(self):
        args = self.value
        kwds = ['{k}={v}'.format(k=k, v=getattr(self, k))
                for k in ('desc', 'units', 'range', 'dtype')]
        return 'ModelParameter({args}, {kwds})'.format(args=args,
                                                       kwds=', '.join(kwds))
