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
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    setup_requires=["setuptools"],
    install_requires=[
        "binaryornot",
        "jinja2",
        "packaging",
        "pyyaml",
        "py-scripting",
        "six",
    ],
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
