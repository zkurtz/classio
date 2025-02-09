"""Class decorator to declare IO methods of class data."""

import inspect
import types
from pathlib import Path
from typing import Any, Type

import packio
from dummio.protocol import assert_module_protocol

from classio.constants import ModulePerAttribute
from classio.inference import infer_io_module, load_requires_model


def _require_type_hints(signature: inspect.Signature) -> None:
    """Require that all parameters in the signature have type hints.

    Args:
        signature: The signature to check.

    Raises:
        ValueError: If any parameter in the signature -- except for "self" -- lacks a type hint.
        ValueError: If any parameter has a Union type hint.
    """
    params = signature.parameters
    for name, param in params.items():
        if name == "self":
            continue
        if param.annotation == inspect._empty:
            raise ValueError(f"Missing type hint for parameter {name}")
        # Check for union types:
        if isinstance(param.annotation, types.UnionType):
            raise ValueError(
                f"Union type hint found for parameter {name}: {param.annotation}"
                ", but declario does not support union types."
            )


def declario(*, io_modules: ModulePerAttribute | None = None) -> Any:
    """Class decorator to declare IO methods of class data.

    Use as a decorator on a class to
      - declare the IO methods for each of the classes data attributes
      - add `save` and `load` methods to the class based on this declaration ...
      - ... such that the IO methods create use only a single file for the entire class.

    Example: Suppose you are defining a class MyData with data attributes `config: dict[str, str]` and
    `df: pd.DataFrame`:

        ```
        import pandas as pd
        import dummio
        import dummio.pandas.df_parquet

        @declario({
            "config": dummio.json,
            "df": dummio.pandas.df_parquet,
        })
        class MyData:
            config: dict[str, str]
            df: pd.DataFrame

        data = MyData(config={"a": "1"}, df=pd.DataFrame({"a": [1, 2, 3]}))
        data.save("data")
        data2 = MyData.from_file("data")
        assert data2.config == {"a": "1"}
        assert data2.df.equals(pd.DataFrame({"a": [1, 2, 3]}))
        ```

    Args:
        cls: The class to decorate.
        io_modules: A dictionary mapping data attribute names to modules containing corresponding save/load methods.
            Each module must have `save` and `load` methods that conform to the dummio protocol for IO modules.

    Raises:
        ValueError: If the set of arguments to the class __init__ is not identical to the set of class attributes
            recorded in the class annotations.
        ValueError: If type hints are absent for any class __init__ arguments.
        ValueError: If the `io_modules` dictionary includes any key that is not the name of a data attribute in
            the decorated class.
    """

    io_modules = io_modules.copy() if io_modules else {}
    # any io modules need to conform to the dummio protocol for IO modules:
    for module in io_modules.values():
        assert_module_protocol(module=module)

    def decorator(cls: Type) -> Any:
        """Decorates the class with IO methods.

        Args:
            cls: The class to decorate.

        Returns:
            The decorated class.
        """
        _require_type_hints(signature=inspect.signature(cls.__init__))
        signature = inspect.signature(cls.__init__).parameters
        arg_names = list(signature)
        arg_names.remove("self")

        # Check that all keys in `io_modules` are valid data attribute names
        invalid_keys = set(io_modules.keys()) - set(arg_names)
        if invalid_keys:
            raise ValueError(f"Invalid keys in `io_modules`: {invalid_keys}")

        annotations = {name: signature[name].annotation for name in arg_names}
        io_per_attribute = {
            name: io_modules.get(name, None) or infer_io_module(name, annotation=annotations[name])
            for name in arg_names
        }

        def save(self, filepath: str | Path) -> None:
            """Saves the class data to a single file."""
            with packio.Writer(Path(filepath)) as writer:
                for name in arg_names:
                    io_module = io_per_attribute[name]
                    data = getattr(self, name)
                    filepath = writer.file(name)
                    io_module.save(data=data, filepath=filepath)

        def load(cls: Type, filepath: str | Path) -> Any:
            """Loads the class data from a single file."""
            data: dict[str, Any] = {}
            with packio.Reader(Path(filepath)) as reader:
                for name in arg_names:
                    annotation = annotations[name]
                    loader = io_per_attribute[name].load
                    filepath = reader.file(name)
                    if load_requires_model(annotation):
                        data[name] = loader(filepath=filepath, model=annotation)
                    else:
                        data[name] = loader(filepath=filepath)
            return cls(**data)

        cls.from_file = classmethod(load)
        cls.save = save
        return cls

    return decorator
