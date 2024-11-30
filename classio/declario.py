"""Class decorator to declare IO methods of class data."""

from typing import Type, Any, Dict
from types import ModuleType
from classio.constants import ModulePerAttribute
from pathlib import Path
import packio
import inspect
import importlib
import types


def _is_dict_annotation(annotation: Any) -> bool:
    """Checks if a type annotation is a dictionary.

    Args:
        annotation: The type annotation to check.
    """
    if hasattr(annotation, "__origin__"):
        return annotation.__origin__ in {dict, Dict}
    return False


def _require_type_hints(signature: inspect.Signature) -> None:
    """Require that all parameters in the signature have type hints.

    Args:
        signature: The signature to check.

    Raises:
        ValueError: If any parameter in the signature -- except for "self" -- lacks a type hint.
        ValueError: If any parameter has a union type hint.
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


def _resolve_io_module(name: str, *, annotation: Any, module: ModuleType | None) -> ModuleType:
    """Deduce the IO module to use based on a type annotation.

    Args:
        name: The name of the attribute.
        annotation: The type annotation of the attribute.
        module: The optional IO module explicitly provided by the user.

    Returns:
        An IO module, having methods `save` and `load`.
    """
    if module:
        return module
    if annotation is str:
        return importlib.import_module("dummio.text")
    elif _is_dict_annotation(annotation):
        return importlib.import_module("dummio.json")
    elif annotation.__module__ == "pandas.core.frame":
        return importlib.import_module("dummio.pandas.df_parquet")
    elif hasattr(annotation, "model_validate_json"):
        return importlib.import_module("dummio.pydantic")
    elif annotation.__name__ == "ModelProto" and annotation.__module__ == "onnx.onnx_ml_pb2":
        return importlib.import_module("dummio.onnx")
    raise ValueError(f"No IO module provided or inferred for {name}: {annotation}")


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
        data2 = MyData.load("data")
        assert data2.config == {"a": "1"}
        assert data2.df.equals(pd.DataFrame({"a": [1, 2, 3]}))
        ```

    Args:
        cls: The class to decorate.
        io_modules: A dictionary mapping data attribute names to modules containing corresponding save/load methods.

    Raises:
        ValueError: If the set of arguments to the class __init__ is not identical to the set of class attributes
            recorded in the class annotations.
        ValueError: If type hints are absent for any class __init__ arguments.
        ValueError: If the `io_modules` dictionary includes any key that is not the name of a data attribute in
            the decorated class.
    """

    io_modules = io_modules.copy() if io_modules else {}

    def decorator(cls: Type) -> Any:
        """Decorates the class with IO methods.

        Args:
            cls: The class to decorate.

        Returns:
            The decorated class.
        """
        _require_type_hints(signature=inspect.signature(cls.__init__))
        signature = inspect.signature(cls.__init__).parameters
        item_names = list(signature)
        item_names.remove("self")
        # Check that all keys in `io_modules` are valid data attribute names
        invalid_keys = set(io_modules.keys()) - set(item_names)
        if invalid_keys:
            raise ValueError(f"Invalid keys in `io_modules`: {invalid_keys}")
        annotations = {name: signature[name].annotation for name in item_names}
        io = {
            name: _resolve_io_module(name, annotation=annotations[name], module=io_modules.get(name, None))
            for name in item_names
        }

        def save(self, filepath: str | Path) -> None:
            """Saves the class data to a single file."""
            with packio.Writer(Path(filepath)) as writer:
                for name in item_names:
                    io[name].save(
                        data=getattr(self, name),
                        filepath=writer.file(name),
                    )

        def load(cls: Type, filepath: str | Path) -> Any:
            """Loads the class data from a single file."""
            data: dict[str, Any] = {}
            with packio.Reader(Path(filepath)) as reader:
                for name in item_names:
                    annotation = annotations[name]
                    if hasattr(annotation, "model_validate_json"):
                        # This is the pydantic case
                        data[name] = io[name].load(filepath=reader.file(name), model=annotation)
                    else:
                        data[name] = io[name].load(filepath=reader.file(name))
            return cls(**data)

        cls.load = classmethod(load)
        cls.save = save
        return cls

    return decorator
