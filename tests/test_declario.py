"""Testing the classio.declario class decorator."""

from dataclasses import dataclass
from pathlib import Path

import dummio
import dummio.pandas.df_parquet
import pandas as pd

from classio import declario


def test_basic_class(tmp_path: Path):
    """A simple class including IO module type inference."""

    @declario()
    class MyData:
        def __init__(self, config: dict[str, str], df: pd.DataFrame) -> None:
            self.config = config
            self.df = df

    data = MyData(config={"a": "1"}, df=pd.DataFrame({"a": [1, 2, 3]}))
    filepath = tmp_path / "data"
    data.save(filepath=filepath)
    data2 = MyData.load(filepath)
    assert data2.config == data.config
    assert data2.df.equals(data.df)


def test_dataclass(tmp_path: Path):
    """A dataclass with user-specified IO modules."""

    @declario(
        io_modules={
            "config": dummio.yaml,
            "df": dummio.pandas.df_parquet,
        }
    )
    @dataclass
    class MyData:
        config: dict[str, str]
        df: pd.DataFrame

    data = MyData(config={"a": "1"}, df=pd.DataFrame({"a": [1, 2, 3]}))
    filepath = tmp_path / "data"
    data.save(filepath=filepath)
    data2 = MyData.load(filepath)
    assert data2.config == data.config
    assert data2.df.equals(data.df)
