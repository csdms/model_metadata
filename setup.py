from setuptools import setup, find_packages

from model_metadata import __version__


def read_requirements():
    import os


    path = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(path, 'requirements.txt')
    try:
        with open(requirements_file, 'r') as req_fp:
            requires = req_fp.read().split()
    except IOError:
        return []
    else:
        return [require.split() for require in requires]


setup(name='model_metadata',
      version=__version__,
      description='Model Metadata',
      author='Eric Hutton',
      author_email='huttone@colorado.edu',
      url='http://csdms.colorado.edu',
      install_requires=read_requirements(),
      setup_requires=['setuptools', ],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'mmd-find=model_metadata.cli.find:main',
              'mmd-stage=model_metadata.cli.stage:main',
              'mmd-meta=model_metadata.cli.meta:main',
          ],
      },
)
