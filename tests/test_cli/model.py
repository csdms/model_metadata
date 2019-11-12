import pathlib


class ModelString:
    METADATA = "."


class ModelPath:
    METADATA = pathlib.Path(".")


class ModelAbsolutePath:
    METADATA = pathlib.Path("/")
