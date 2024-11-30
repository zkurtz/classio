"""Basic IO utilities."""

from pathlib import Path
from types import ModuleType
from typing import TypeAlias

PathType: TypeAlias = str | Path
ModulePerAttribute: TypeAlias = dict[str, ModuleType]
