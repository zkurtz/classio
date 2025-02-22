"""Testing the classio.declario class decorator with array-type attributes."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from classio import declario


def test_with_arrays(tmp_path: Path):
    @declario()
    @dataclass
    class MyData:
        df: pd.DataFrame
        series: pd.Series
        matrix: np.ndarray

    data = MyData(df=pd.DataFrame({"a": [1, 2, 3]}), series=pd.Series([1, 2, 3]), matrix=np.array([[1, 2], [3, 4]]))
    filepath = tmp_path / "data"
    data.save(filepath=filepath)
    data2 = MyData.from_file(filepath)
    assert data2.df.equals(data.df)
    assert data2.series.equals(data.series)
    assert np.array_equal(data2.matrix, data.matrix)
