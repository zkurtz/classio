# classio

IO tools for python classes.

This project simplifies IO for data classes while following these principles:
- Cross-platform/version compatibility matters → avoid pickle.
- A single file is simpler to manage than a directory → keep a 1-1 relationship between classes and files. We use [packio](https://github.com/zkurtz/packio) to achieve this.
- Users should not need to write boilerplate IO methods → we rely on [dummio](https://github.com/zkurtz/dummio) for a standardized interface to numerous IO methods.


[on pypi](https://pypi.org/project/classio/): `pip install classio`.


## "declare IO" decorator

Apply the `classio.declario` decorator to a class to add `save(filepath)` and `from_file(filepath)` methods to the class. For many classes and common attribute types, the decorator is able to automatically detecting and applying appropriate serialization methods for each class attribute based on type annotations:
```
import pandas as pd
from dataclasses import dataclass
from classio import declario

@declario()
@dataclass
class MyData:
    config: dict[str, str]
    df: pd.DataFrame

# Create an instance of the class:
data = MyData(config={"a": "1"}, df=pd.DataFrame({"a": [1, 2, 3]}))

# IO cycle:
filepath = tmp_path / "data"
data.save(filepath)
data2 = MyData.from_file(filepath)

# Check that the data was preserved:
assert data2.config == data.config
assert data2.df.equals(data.df)
```

## How it works

The `declario` decorator technically could work with a general python class, but is designed primarily to be used with `dataclasses.dataclass` or `attrs` classes. A decorated class
- saves/loads only the class attributes corresponding to the names of the arguments the class constructor (`__init__`), and uses the class `__init__` method to construct a new class instance on `from_file`.
- raises a ValueError if any `__init__` argument is missing a type annotation.
- raises a ValueError if any `__init__` argument has a Union type (i.e. `int | str`; you must use just one type per argument).

`declario` does not intrinsically guarantee exact equality of objects across IO cycles. For example, a UUID value in a class attribute of type `dict` may be serialized as a string, and then deserialized as a string, which may not be equal to the original UUID object. This is a limitation of the serialization methods used, not of `classio` itself. It is up to the user to ensure that the serialization methods used are appropriate for the class attributes they are applied to.

`classio` minimizes the set or required dependencies. If you encounter errors, a reasonable first thing to check is whether you have all required dependencies installed for any IO methods getting called for your class attributes. For example, if you have a class attribute of type `pandas.DataFrame`, you will need to install `pandas`. See the dependency groups organized by IO type in `pyproject.toml`.

## Custom IO methods

The `declario` decorator can be customized with the `io_modules` argument to specify the IO methods to use for each attribute. In the example above, `config` automatically gets serialized using json, but we could tell it to use yaml instead:
```
import dummio.yaml
from uuid import UUID

@declario(io_modules={"config": dummio.yaml})
@dataclass
class MyData:
    config: dict[str, str | int | UUID]
    ...
```

However, neither `yaml` nor `json` necessarily preserve types (such as UUIDs) across IO cycles, loading the values as `str` instead of `UUID`, for example. To address this, you could either
- define a custom IO module for your class attribute and pass it in using `io_modules` argument
- or [recommended when feasible] wrap attributes inside of a pydantic or mashumaro model, as shown in the next sections below:

## pydantic attributes

```
from pydantic import BaseModel

class Config(BaseModel):
    a: str
    b: int
    c: UUID

@declario()
@dataclass
class MyData:
    config: Config
    ...
```
Here, `declario` automatically leverages the `pydantic` IO methods under the hood, preserving data types such as UUIDs across IO cycles.

### mashumaro attributes

`declario` can infer appropriate IO methods for [mashumaro](https://github.com/Fatal1ty/mashumaro) using yaml and json models as well. This works almost identically as the pydantic example; just replace `BaseModel` with `from mashumaro.mixins.yaml import DataClassYAMLMixin` or `from mashumaro.mixins.json import DataClassJSONLMixin`.


## Development

Consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543) if working directly on this repo.
