# model_metadata

![[Python][pypi-link]][python-badge]
![[Build Status][build-link]][build-badge]
![[PyPI][pypi-link]][pypi-badge]
![[Build Status][anaconda-link]][anaconda-badge]

[anaconda-badge]: https://anaconda.org/conda-forge/model_metadata/badges/version.svg
[anaconda-link]: https://anaconda.org/conda-forge/model_metadata
[build-badge]: https://github.com/csdms/model_metadata/actions/workflows/test.yml/badge.svg
[build-link]: https://github.com/csdms/model_metadata/actions/workflows/test.yml
[pypi-badge]: https://badge.fury.io/py/model_metadata.svg
[pypi-link]: https://pypi.org/project/model_metadata/
[python-badge]: https://img.shields.io/pypi/pyversions/model_metadata.svg

Tools for working with CSDMS Model Metadata

The CSDMS Model Metadata provides a detailed and formalized description
of a model. This includes information about:

- Identifying information about the model. For example, model
  author(s), citations for the model, URL to the source code, etc.
- A description of the model API, if it has been wrapped with a Basic
  Model Interface. This includes, for instance, how to build the model,
  depending on the language, what include statements are needed, etc.
- A description of input file parameters. This includes default values,
  acceptable parameter ranges, units, etc.
- Template input files. These are a set of input files that contain
  special markup where parameters from the metadata parameter
  description can be placed.
- A description of how to run the model from the command line.

The CSDMS Model Metadata is extensible and not yet complete. New
metadata will most certainly be added in the future. We believe the
current specification provides a minimum amount of information needed to
describe a model to be either run as a standalone model or, possibly, to
couple with another model.

Whereas the BMI answers run-time queries of a model (e.g. the current
time of a model simulation, the value of a particular output variable),
the CSDMS Model Metadata provides a static description of a model. The
Model Metadata, along with a BMI implementation, allows a model to
automatically be incorporated as a component in the CSDMS PyMT.

## Info section

Identifying information about the model.

```yaml
info:
    summary:
      Sedflux3D is a basin filling stratigraphic model. Sedflux3d simulates
      long-term marine sediment transport and accumulation into a
      three-dimensional basin over time scales of tens of thousands of years. It
      simulates the dynamics of strata formation of continental margins based on
      distribution of river plumes and tectonics.
    url: http://csdms.colorado.edu/wiki/Model_help:Sedflux
    author: Eric Hutton
    email: eric.hutton@colorado.edu
    version: "2.1"
    license: MIT
    doi: "10.1594/IEDA/100161"
    cite_as: |
      @article{hutton2008sedflux,
      title={Sedflux 2.0: An advanced process-response model that generates three-dimensional stratigraphy},
      author={Hutton, Eric WH and Syvitski, James PM},
      journal={Computers \& Geosciences},
      volume={34},
      number={10},
      pages={1319--1337},
      year={2008},
      publisher={Pergamon}
      }
```

## API Section

A description of the model API.

```yaml
api:
    name: Sedflux3D
    language: c
    register: register_bmi_sedflux3d
    includes:
      - "#include <sedflux3d/bmi_sedflux3d.h>"
    cflags:
      pkgconfig: sedflux3d
    libs:
      pkgconfig: sedflux3d
```

## Parameters Section

A description of the parameters in the input files.

```yaml
parameters:
    slope_gradient:
      description: Gradient of slope
      value:
        default: 0.01
        range:
          max: 0.1
          min: 0.0
        type: float
        units: m

    shelf_width:
      description: Width of shelf
      value:
        default: 100000.0
        range:
          max: 1000000.0
          min: 1000.0
        type: float
        units: m
```

## Run Section

How the model is to be run.

```yaml
run:
    config_file: sedflux_3d_init.kvf
```

# Model Metadata Tools

The CSDMS *model_metadata* Python package provides tools for working
with CSDMS Model Metadata. Contained within this package are tools for:

- Reading and parsing model metadata that follow the CSDMS Model
  Metadata Standards.
- Setting up model simulations either programmatically or through a
  commandline interface. Although model metadata may describe models
  with different interfaces, the model metadata tools provides a common
  interface for staging simulations.
- Validing input parameter units, ranges, and type checking. If, for
  instance, a user provides an input value that is out of range, an
  error can be issued.
- Running simulations, which have already been staged, through a common
  interface.

These tools are currently used by:

- The Web Modeling Tool server to validate input parameters and stage
  model simulations.
- The CSDMS Execution Server and PyMT for running BMI-enabled models.
- Commandline utilities for quering model metadata, and staging model
  simulations.
