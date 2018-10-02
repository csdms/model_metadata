from setuptools import setup, find_packages

import versioneer


def read_requirements():
    import os

    path = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(path, "requirements.txt")
    try:
        with open(requirements_file, "r") as req_fp:
            requires = req_fp.read().split()
    except IOError:
        return []
    else:
        return [require.split() for require in requires]


setup(
    name="model_metadata",
    version=versioneer.get_version(),
    description="Model Metadata",
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    setup_requires=["setuptools"],
    packages=find_packages(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        "console_scripts": [
            "mmd=model_metadata.cli.main:main",
            "mmd-find=model_metadata.cli.main_find:main",
            "mmd-stage=model_metadata.cli.main_stage:main",
            "mmd-dump=model_metadata.cli.main_dump:main",
            "mmd-install=model_metadata.cli.main_install:main",
            "mmd-query=model_metadata.cli.main_query:main",
        ],
        "bmi.plugins": ["bmi_mmd=model_metadata.cli.main:configure_parser_mmd"],
    },
)
