# classio

IO tools for python classes.

This project simplifies the creation of IO methods for complex objects while following these principles:
- Cross-platform/version compatibility matters → avoid pickle.
- A single file is simpler to manage than a directory → keep a 1-1 relationship between classes and files. We use [packio](https://github.com/zkurtz/packio) to achieve this.
- Users should not need to write boilerplate IO methods → we rely on [dummio](https://github.com/zkurtz/dummio) for a standardized interface to numerous IO methods.


[On pypi](https://pypi.org/project/classio/): `pip install classio`.


## Example

```
from dataclasses import dataclass
import pandas as pd
import dummio
import dummio.pandas.df_parquet
from classio import Declario

@Declario(
    {
        "config": dummio.json,
        "df": dummio.pandas.df_parquet,
    }
)
@dataclass()
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
