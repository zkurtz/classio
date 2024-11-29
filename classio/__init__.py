"""Public methods and classes for packio package."""

from importlib.metadata import version

from classio.declario import declario

__version__ = version("classio")
__all__ = ["declario"]
