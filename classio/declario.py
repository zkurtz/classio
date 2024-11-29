"""Class decorator to declare IO methods of class data."""

from typing import Type, Any
from classio.constants import ModulePerAttribute
from pathlib import Path
import packio


def declario(*, io_modules: ModulePerAttribute) -> Any:
    """Class decorator to declare IO methods of class data.

    Use as a decorator on a class to
      - declare the IO methods for each of the classes data attributes
      - add `save` and `load` methods to the class based on this declaration
      - such that the IO methods create use only a single file for the entire class.

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

    Attributes:
        io_modules: A dictionary mapping data attribute names to modules containing corresponding save/load methods.

    Raises:
        ValueError: If the `io_modules` dictionary includes any key that is not the name of a data attribute in
            the decorated class.
    """

    def decorator(cls: Type) -> Any:
        """Decorates the class with IO methods.

        Args:
            cls: The class to decorate.

        Returns:
            The decorated class.
        """

        # Check that all keys in `io_modules` are valid data attribute names
        invalid_keys = set(io_modules.keys()) - set(cls.__annotations__.keys())
        if invalid_keys:
            raise ValueError(f"Invalid keys in `io_modules`: {invalid_keys}")

        def save(self, filepath: str | Path) -> None:
            """Saves the class data to a single file."""
            with packio.Writer(Path(filepath)) as writer:
                for attr_name, io_module in io_modules.items():
                    io_module.save(
                        data=getattr(self, attr_name),
                        filepath=writer.file(attr_name),
                    )

        def load(cls: Type, filepath: str | Path) -> Any:
            """Loads the class data from a single file."""
            with packio.Reader(Path(filepath)) as reader:
                data = {
                    attr_name: io_module.load(filepath=reader.file(attr_name))
                    for attr_name, io_module in io_modules.items()
                }
                return cls(**data)

        cls.load = classmethod(load)
        cls.save = save
        return cls

    return decorator  # Return the inner decorator function
