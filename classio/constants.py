"""Basic IO utilities."""

from pathlib import Path
from typing import TypeAlias
from types import ModuleType


PathType: TypeAlias = str | Path
ModulePerAttribute: TypeAlias = dict[str, ModuleType]
