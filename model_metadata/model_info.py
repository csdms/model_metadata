#! /usr/bin/env python
import re
import warnings
from pprint import pformat

import six
import yaml
from packaging.version import InvalidVersion, Version

from .load import load_meta_section
from .model_parameter import setup_yaml_with_canonical_dict

setup_yaml_with_canonical_dict()


EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
DOI_REGEX = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'


def norm_authors(authors):
    """Normalize a list of author names.

    Parameters
    ----------
    authors : str or iterable of str
        Author name of list of author names.

    Returns
    -------
    list of str
        List of author names as `First Last`.

    Examples
    --------
    >>> from model_metadata.model_info import norm_authors

    >>> norm_authors('Cleese, John')
    ['John Cleese']

    >>> norm_authors('John Cleese and Gilliam, Terry')
    ['John Cleese', 'Terry Gilliam']

    >>> norm_authors(['John Cleese', 'Terry Gilliam', 'Idle, Eric'])
    ['John Cleese', 'Terry Gilliam', 'Eric Idle']
    """
    if isinstance(authors, six.string_types):
        authors = authors.split(" and ")

    normed = []
    for author in authors:
        try:
            last, first = author.split(",")
        except ValueError:
            pass
        else:
            author = " ".join([first.strip(), last.strip()])
        finally:
            normed.append(author)

    return normed


def validate_email(email):
    """Validate an email address string.

    Parameters
    ----------
    email : str
        Email address.

    Raises
    ------
    ValueError
        If the email address is not valid.

    Returns
    -------
    str
        The email address.

    Examples
    --------
    >>> from model_metadata.model_info import validate_email
    >>> validate_email('Graham.Chapman@montypython.com')
    'Graham.Chapman@montypython.com'

    >>> validate_email('Terry.Jones@monty') #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: Terry.Jones@monty: invalid email address
    """
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("{email}: invalid email address".format(email=email))
    return email


def validate_url(url):
    """Validate a URL string."""
    if not re.match(URL_REGEX, url):
        raise ValueError("{url}: invalid URL".format(url=url))
    return url


def validate_doi(doi):
    """Validate a DOI string."""
    if not re.match(DOI_REGEX, doi):
        raise ValueError("{doi}: invalid DOI".format(doi=doi))
    return doi


def validate_version(version):
    """Validate a version string."""
    try:
        Version(version)
    except InvalidVersion:
        warnings.warn("{v}: version string does not follow PEP440".format(v=version))
    return version


def validate_is_str(s):
    if isinstance(s, six.string_types):
        return s
    else:
        raise TypeError("not a string")


def object_properties(obj):
    import inspect

    properties = inspect.getmembers(obj.__class__, lambda o: isinstance(o, property))

    props = []
    for name, _ in properties:
        props.append((name, getattr(obj, name)))
    return props


class ModelInfo(object):

    """Information about a model."""

    def __init__(
        self,
        name,
        author=None,
        email=None,
        version=None,
        license=None,
        doi=None,
        url=None,
        summary=None,
        cite_as=None,
    ):
        if isinstance(cite_as, six.string_types):
            cite_as = [cite_as]

        self._name = name

        version = str(version)

        self._authors = author and tuple(norm_authors(author)) or ()
        self._cite_as = cite_as and tuple(cite_as) or ()
        self._email = email and validate_email(email) or None
        self._doi = doi and validate_doi(doi) or None
        self._url = url and validate_url(url) or None
        self._version = version and validate_version(version) or None
        self._license = license and validate_is_str(license) or None
        self._summary = summary and validate_is_str(summary) or None

    @property
    def name(self):
        return self._name

    @property
    def authors(self):
        return self._authors

    @property
    def cite_as(self):
        return self._cite_as

    @property
    def email(self):
        return self._email

    @property
    def version(self):
        return self._version

    @property
    def license(self):
        return self._license

    @property
    def doi(self):
        return self._doi

    @property
    def url(self):
        return self._url

    @property
    def summary(self):
        return self._summary

    def as_dict(self):
        return dict(object_properties(self))

    @classmethod
    def from_dict(cls, params):
        name = params.pop("name", "?")
        return cls(name, **params)

    @classmethod
    def from_path(cls, path):
        params = load_meta_section(path, "info")
        return cls.from_dict(params)

    @staticmethod
    def norm(params):
        for key in ("initialize_args", "class", "id"):
            if params.pop(key, None):
                warnings.warn("ignoring '{0}' in info section".format(key))
        name = params.pop("name", "?")
        return ModelInfo(name, **params).as_dict()

    def to_yaml(self):
        d = self.as_dict()
        d["authors"] = list(d.get("authors", []))
        d["cite_as"] = list(d.get("cite_as", []))
        return yaml.safe_dump(d, default_flow_style=False)

    def __str__(self):
        return pformat(object_properties(self))
