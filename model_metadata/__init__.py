import pkg_resources

from .model_parameter import ModelParameter
from .model_info import ModelInfo
from .modelmetadata import ModelMetadata
from .errors import MetadataNotFoundError
from .utils import install_mmd, get_cmdclass, get_entry_points


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
