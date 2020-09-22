Changelog for model_metadata
============================

0.7.0 (2020-09-22)
------------------

- Added constructor for ModelMetadata that accepts an object rather than
  a string, better searching for metadata.


0.6.2 (2020-09-17)
------------------

- Fixed a bug that raised "object has no attribute '__module__'"
  exception when looking for metadata of an instance from an
  extension module (#22)


0.6.1 (2020-09-01)
------------------

- Removed versioneer; use zest.releaser instead


0.6.0 (2019-11-12)
------------------

- Changed command line interface to use click (#20)


0.5.0 (2019-05-15)
------------------

- Query a model by class or name


0.4.4 (2019-04-09)
------------------

- Deploy to PyPI from Travis

- Fixed continuous integration on Travis

- General package clean up


0.4.3 (2019-03-15)
------------------

- Fixed a bug where the yaml loader failed to correctly parse
  numbers represented in scientific notation

0.4.2 (2018-10-08)
------------------

- Fixed a typo in mmd-stage command that caused it to crash
