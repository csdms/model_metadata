#! /usr/bin/env python
from __future__ import annotations

import inspect
import re
import warnings
from collections.abc import Iterable
from pprint import pformat
from typing import Any

import yaml
from model_metadata.load import load_meta_section
from model_metadata.model_parameter import setup_yaml_with_canonical_dict
from packaging.version import InvalidVersion
from packaging.version import Version

setup_yaml_with_canonical_dict()


EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
DOI_REGEX = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'


def norm_authors(authors: str | Iterable[str]) -> tuple[str, ...]:
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
    ('John Cleese',)

    >>> norm_authors('John Cleese and Gilliam, Terry')
    ('John Cleese', 'Terry Gilliam')

    >>> norm_authors(['John Cleese', 'Terry Gilliam', 'Idle, Eric'])
    ('John Cleese', 'Terry Gilliam', 'Eric Idle')
    """
    if isinstance(authors, str):
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

    return tuple(normed)


def validate_email(email: str) -> str:
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
        raise ValueError(f"{email}: invalid email address")
    return email


def validate_url(url: str) -> str:
    """Validate a URL string."""
    if not re.match(URL_REGEX, url):
        raise ValueError(f"{url}: invalid URL")
    return url


def validate_doi(doi: str) -> str:
    """Validate a DOI string."""
    if not re.match(DOI_REGEX, doi):
        raise ValueError(f"{doi}: invalid DOI")
    return doi


def validate_version(version: str) -> str:
    """Validate a version string."""
    try:
        Version(version)
    except InvalidVersion:
        warnings.warn(f"{version}: version string does not follow PEP440", stacklevel=2)
    return version


def validate_is_str(s: Any) -> str:
    if isinstance(s, str):
        return s
    else:
        raise TypeError("not a string")


def object_properties(obj: ModelInfo) -> tuple[tuple[str, Any], ...]:
    properties = inspect.getmembers(obj.__class__, lambda o: isinstance(o, property))
    return tuple((name, getattr(obj, name)) for name, _ in properties)


class ModelInfo:
    """Information about a model."""

    def __init__(
        self,
        name: str,
        author: str | None = None,
        email: str | None = None,
        version: str | None = None,
        license: str | None = None,
        doi: str | None = None,
        url: str | None = None,
        summary: str | None = None,
        cite_as: str | Iterable[str] | None = None,
    ):
        if isinstance(cite_as, str):
            self._cite_as: tuple[str, ...] | tuple[()] = (cite_as,)
        elif cite_as is None:
            self._cite_as = ()
        else:
            self._cite_as = tuple(cite_as)

        self._name = name

        version = str(version)

        self._authors = author and tuple(norm_authors(author)) or ()
        self._email = email and validate_email(email) or None
        self._doi = doi and validate_doi(doi) or None
        self._url = url and validate_url(url) or None
        self._version = version and validate_version(version) or None
        self._license = license and validate_is_str(license) or None
        self._summary = summary and validate_is_str(summary) or None

    @property
    def name(self) -> str:
        return self._name

    @property
    def authors(self) -> tuple[str, ...]:
        return self._authors

    @property
    def cite_as(self) -> tuple[str, ...]:
        return self._cite_as

    @property
    def email(self) -> str | None:
        return self._email

    @property
    def version(self) -> str | None:
        return self._version

    @property
    def license(self) -> str | None:
        return self._license

    @property
    def doi(self) -> str | None:
        return self._doi

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def summary(self) -> str | None:
        return self._summary

    def as_dict(self) -> dict[str, Any]:
        return dict(object_properties(self))

    @classmethod
    def from_dict(cls, params: dict[str, Any]) -> ModelInfo:
        return cls(params.pop("name", "?"), **params)

    @classmethod
    def from_path(cls, path: str) -> ModelInfo:
        return cls.from_dict(load_meta_section(path, "info"))

    @staticmethod
    def norm(params: dict[str, Any]) -> dict[str, Any]:
        for key in ("initialize_args", "class", "id"):
            if params.pop(key, None):
                warnings.warn(f"ignoring '{key}' in info section", stacklevel=2)
        return ModelInfo(params.pop("name", "?"), **params).as_dict()

    def to_yaml(self) -> str:
        d = self.as_dict()
        d["authors"] = d.get("authors", ())
        d["cite_as"] = d.get("cite_as", ())
        return yaml.safe_dump(d, default_flow_style=False)

    def __str__(self) -> str:
        return pformat(object_properties(self))
