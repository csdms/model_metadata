from .model_parameter import ModelParameter
from .model_info import ModelInfo
from .modelmetadata import ModelMetadata
from .errors import MetadataNotFoundError
from .utils import install_mmd, get_cmdclass, get_entry_points


__all__ = [
    "ModelParameter",
    "ModelInfo",
    "ModelMetadata",
    "MetadataNotFoundError",
    "install_mmd",
    "get_cmdclass",
    "get_entry_points",
]
__version__ = "0.1"

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
