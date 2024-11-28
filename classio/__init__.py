"""Public methods and classes for packio package."""

from importlib.metadata import version

from classio.decorators import Declario

__version__ = version("classio")
__all__ = ["Declario"]
