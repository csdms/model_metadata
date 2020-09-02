from setuptools import setup, find_packages


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [
        read('README.rst'),
        read('AUTHORS.rst'),
        read('CHANGES.rst'),
    ]
)

setup(
    name="model_metadata",
    version="0.6.1",
    description="Model Metadata",
    long_description=long_description,
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    classifiers=[
        "Development Status :: 4 - Beta",
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
    keywords=["bmi", "pymt"],
    setup_requires=["setuptools"],
    install_requires=open("requirements.txt", "r").read().splitlines(),
    packages=find_packages(),
    entry_points={
        "console_scripts": ["mmd=model_metadata.cli.main:mmd"],
        "bmi.plugins": ["bmi_mmd=model_metadata.cli.main:configure_parser_mmd"],
    },
)
