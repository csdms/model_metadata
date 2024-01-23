from __future__ import annotations

import contextlib
import importlib
import os
import re
import sys
from collections.abc import Iterable
from typing import Any

import click
from model_metadata.api import find as _find
from model_metadata.api import query as _query
from model_metadata.api import stage as _stage
from model_metadata.errors import MetadataNotFoundError
from model_metadata.errors import MissingSectionError
from model_metadata.errors import MissingValueError
from model_metadata.modelmetadata import ModelMetadata


class MetadataLocationParamType(click.Path):
    name = "metadata"

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> Any:
        try:
            validate_entry_point(ctx, param, value)
        except (ValueError, click.BadParameter):
            model = value
        else:
            model = _find(load_component(value))

        for p in ModelMetadata.search_paths(model):
            with contextlib.suppress(Exception):
                return super().convert(p, param, ctx)

        return super().convert(value, param, ctx)


def validate_entry_point(
    ctx: click.Context | None,
    param: click.Parameter | None,
    value: str | None,
) -> str | None:
    MODULE_REGEX = r"^(?!.*\.\.)(?!.*\.$)[A-Za-z][\w\.]*$"
    CLASS_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
    if value is not None:
        try:
            module_name, class_name = str(value).split(":")
        except ValueError:
            raise click.BadParameter(
                "Bad entry point", param=param, param_hint="module_name:ClassName"
            )
        if not re.match(MODULE_REGEX, module_name):
            raise click.BadParameter(
                f"Bad module name ({module_name})",
                param_hint="module_name:ClassName",
            )
        if not re.match(CLASS_REGEX, class_name):
            raise click.BadParameter(
                f"Bad class name ({class_name})",
                param_hint="module_name:ClassName",
            )
    return value


def load_component(entry_point: str) -> type[Any]:
    if "" not in sys.path:
        sys.path.append("")

    module_name, cls_name = entry_point.split(":")

    component = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise
    else:
        try:
            component = module.__dict__[cls_name]
        except KeyError:
            raise ImportError(cls_name)

    return component


@click.group()
@click.version_option()
def mmd() -> None:
    pass


@mmd.command()
@click.argument(
    "metadata",
    type=MetadataLocationParamType(
        exists=True, file_okay=False, dir_okay=True, writable=False, resolve_path=True
    ),
)
def find(metadata: str) -> None:
    sys.path.append("")
    try:
        click.secho(str(_find(metadata)), err=False)
    except MetadataNotFoundError:
        sys.exit(1)
    else:
        sys.exit(0)


@mmd.command()
@click.argument(
    "metadata",
    type=MetadataLocationParamType(
        exists=True, file_okay=False, dir_okay=True, writable=False, resolve_path=True
    ),
)
@click.option("--var", multiple=True, help="name of variable or section")
@click.option("--all", is_flag=True, help="query all sections")
def query(metadata: str, var: Iterable[str], all: bool) -> None:
    if all:
        vars: Iterable[str] = ModelMetadata.SECTIONS
    else:
        vars = var

    values, errors = {}, {}
    for name in vars:
        try:
            value = _query(metadata, name)
        except MissingSectionError as err:
            errors[name] = f"{err.name}: Missing section"
        except MissingValueError as err:
            errors[name] = f"{err.name}: Missing value"
        else:
            values[name] = value

    if errors:
        for error in errors.values():
            click.secho(error, err=True, fg="red")
    else:
        click.echo_via_pager(ModelMetadata.format(values))

    sys.exit(len(errors))


@mmd.command()
@click.argument(
    "metadata",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=False, resolve_path=True
    ),
)
@click.argument(
    "dest",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, resolve_path=True
    ),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="supress printing the manifest to the screen",
)
@click.option("--old-style-templates", is_flag=True, help="use old-style templates")
def stage(metadata: str, dest: str, quiet: bool, old_style_templates: bool) -> None:
    try:
        manifest = _stage(metadata, dest=dest, old_style_templates=old_style_templates)
    except MetadataNotFoundError as err:
        click.secho(str(err), err=True)
        sys.exit(1)

    if not quiet:
        click.secho(os.linesep.join(manifest), err=False)
    sys.exit(0)
