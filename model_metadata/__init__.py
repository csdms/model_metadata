import pkg_resources

from .errors import MetadataNotFoundError
from .model_info import ModelInfo
from .model_parameter import ModelParameter
from .modelmetadata import ModelMetadata
from .utils import get_cmdclass, get_entry_points, install_mmd

__version__ = pkg_resources.get_distribution("model_metadata").version
__all__ = [
    "ModelParameter",
    "ModelInfo",
    "ModelMetadata",
    "MetadataNotFoundError",
    "install_mmd",
    "get_cmdclass",
    "get_entry_points",
]
