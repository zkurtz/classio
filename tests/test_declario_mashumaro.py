"""Testing the classio.declario class decorator involving a mashumaro attribute."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd
from mashumaro.mixins.yaml import DataClassYAMLMixin

from classio import declario


class Currency(Enum):
    """Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md."""

    USD = "USD"
    EUR = "EUR"


@dataclass
class CurrencyPosition:
    """Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md."""

    currency: Currency
    balance: float


@dataclass
class StockPosition:
    """Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md."""

    ticker: str
    name: str
    balance: int


def test_with_mashumaro_yaml(tmp_path: Path):
    """A simple class including a mashumaro attribute."""

    @dataclass
    class Portfolio(DataClassYAMLMixin):
        """Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md."""

        currencies: list[CurrencyPosition]
        stocks: list[StockPosition]

    @declario()
    @dataclass
    class MyData:
        portfolio: Portfolio
        df: pd.DataFrame

    portfolio = Portfolio(
        # Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md:
        currencies=[
            CurrencyPosition(Currency.USD, 238.67),
            CurrencyPosition(Currency.EUR, 361.84),
        ],
        stocks=[
            StockPosition("AAPL", "Apple", 10),
            StockPosition("AMZN", "Amazon", 10),
        ],
    )
    data = MyData(portfolio=portfolio, df=pd.DataFrame({"a": [1, 2, 3]}))
    filepath = tmp_path / "data"
    data.save(filepath=filepath)
    data2 = MyData.from_file(filepath)
    assert data2.portfolio == data.portfolio
    assert data2.df.equals(data.df)


def test_with_mashumaro_json(tmp_path: Path):
    """A simple class including a mashumaro attribute."""

    @dataclass
    class Portfolio(DataClassYAMLMixin):
        """Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md."""

        currencies: list[CurrencyPosition]
        stocks: list[StockPosition]

    @declario()
    @dataclass
    class MyData:
        portfolio: Portfolio
        df: pd.DataFrame

    portfolio = Portfolio(
        # Example copied from https://github.com/Fatal1ty/mashumaro/blob/master/README.md:
        currencies=[
            CurrencyPosition(Currency.USD, 238.67),
            CurrencyPosition(Currency.EUR, 361.84),
        ],
        stocks=[
            StockPosition("AAPL", "Apple", 10),
            StockPosition("AMZN", "Amazon", 10),
        ],
    )
    data = MyData(portfolio=portfolio, df=pd.DataFrame({"a": [1, 2, 3]}))
    filepath = tmp_path / "data"
    data.save(filepath=filepath)
    data2 = MyData.from_file(filepath)
    assert data2.portfolio == data.portfolio
    assert data2.df.equals(data.df)
