"""Testing the classio.declario class decorator."""

from dataclasses import dataclass
import pandas as pd
import dummio
import dummio.pandas.df_parquet
from classio import Declario
from pathlib import Path


def test_declario(tmp_path: Path):
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
