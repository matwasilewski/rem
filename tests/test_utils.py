import pandas as pd

from rem import utils


def test_load_data() -> None:
    loaded_data = utils.load_data('warszawa-sprzedaz.csv')
    assert isinstance(loaded_data, pd.DataFrame)