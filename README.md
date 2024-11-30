# classio

IO tools for python classes.

This project simplifies IO for complex objects while following these principles:
- Cross-platform/version compatibility matters → avoid pickle.
- A single file is simpler to manage than a directory → keep a 1-1 relationship between classes and files. We use [packio](https://github.com/zkurtz/packio) to achieve this.
- Users should not need to write boilerplate IO methods → we rely on [dummio](https://github.com/zkurtz/dummio) for a standardized interface to numerous IO methods.


[On pypi](https://pypi.org/project/classio/): `pip install classio`.


## Examples

## Basic usage

Applying the `classio.declario` decorator to a class adds `save` and `load` methods to the class, automatically detecting and applying appropriate serialization methods for each class attribute:
```
from dataclasses import dataclass
import pandas as pd
from classio import declario

@declario()
@dataclass
class MyData:
    config: dict[str, str]
    df: pd.DataFrame

data = MyData(config={"a": "1"}, df=pd.DataFrame({"a": [1, 2, 3]}))
filepath = tmp_path / "data"
data.save(filepath)
data2 = MyData.load(filepath)
assert data2.config == data.config
assert data2.df.equals(data.df)
```

## Advanced usage

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
- or [recommended when feasible] wrap attributes inside of a pydantic class:

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


## Details and limitations

The `declario` decorator
- is not limited to dataclasses.
- saves/loads only the class attributes corresponding to the names of `__init__` arguments, and uses the class `__init__` method to construct a new class instance on `load`.
- raises a ValueError if any `__init__` argument is missing a type annotation.
- raises a ValueError if any `__init__` argument has a Union type (i.e. `int | str`; you must use just one type per argument).

Warning: `declario` does not *intrinsically* guarantee exact equality of objects across IO cycles. For example, a UUID value in a class attribute of type `dict` may be serialized as a string, and then deserialized as a string, which may not be equal to the original UUID object. This is a limitation of the serialization methods used, not of `classio` itself. It is up to the user to ensure that the serialization methods used are appropriate for the class attributes they are applied to.


## Development

Create and activate a virtual env for dev ops:
```
git clone git@github.com:zkurtz/classio.git
cd classio
pip install uv
uv sync
source .venv/bin/activate
pre-commit install
```
