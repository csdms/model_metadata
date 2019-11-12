import importlib
import os
import re
import sys

import click

from ..api import query as _query, stage as _stage, find as _find, _search_paths
from ..errors import MetadataNotFoundError, MissingSectionError, MissingValueError
from ..modelmetadata import ModelMetadata


class MetadataLocationParamType(click.Path):
    name = "metadata"

    def convert(self, value, param, ctx):

        try:
            validate_entry_point(ctx, param, value)
        except (ValueError, click.BadParameter):
            model = value
        else:
            model = _find(load_component(value))

        for p in _search_paths(model):
            try:
                return super(MetadataLocationParamType, self).convert(p, param, ctx)
            except Exception:
                pass

        return super(MetadataLocationParamType, self).convert(value, param, ctx)

        try:
            return super(MetadataLocationParamType, self).convert(value, param, ctx)
        except Exception:
            raise


def validate_entry_point(ctx, param, value):
    MODULE_REGEX = r"^(?!.*\.\.)(?!.*\.$)[A-Za-z][\w\.]*$"
    CLASS_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
    if value is not None:
        try:
            module_name, class_name = value.split(":")
        except ValueError:
            raise click.BadParameter(
                "Bad entry point", param=value, param_hint="module_name:ClassName"
            )
        if not re.match(MODULE_REGEX, module_name):
            raise click.BadParameter(
                "Bad module name ({0})".format(module_name),
                param_hint="module_name:ClassName",
            )
        if not re.match(CLASS_REGEX, class_name):
            raise click.BadParameter(
                "Bad class name ({0})".format(class_name),
                param_hint="module_name:ClassName",
            )
    return value


def load_component(entry_point):
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
def mmd():
    pass


@mmd.command()
@click.argument(
    "metadata",
    type=MetadataLocationParamType(
        exists=True, file_okay=False, dir_okay=True, writable=False, resolve_path=True
    ),
)
def find(metadata):
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
def query(metadata, var, all):
    if all:
        vars = ModelMetadata.SECTIONS
    else:
        vars = var

    values, errors = {}, {}
    for name in vars:
        try:
            value = _query(metadata, name)
        except MissingSectionError as err:
            errors[name] = "{0}: Missing section".format(err.name)
        except MissingValueError as err:
            errors[name] = "{0}: Missing value".format(err.name)
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
def stage(metadata, dest, quiet, old_style_templates):
    try:
        manifest = _stage(
            metadata, dest=dest, old_style_templates=old_style_templates
        )
    except MetadataNotFoundError as err:
        click.secho(err, err=True)
        sys.exit(1)

    if not quiet:
        click.secho(os.linesep.join(manifest), err=False)
    sys.exit(0)
