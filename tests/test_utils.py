import os

import pandas as pd

from rem import utils


def test_load_data() -> None:
    loaded_data = utils.load_data('warszawa-sprzedaz.csv', "resources")
    assert isinstance(loaded_data, pd.DataFrame)


def test_save_data() -> None:
    test_data = pd.DataFrame({"test": [1, 2, 3]})

    path = os.sep.join(["resources", "test-save-and-load.csv"])
    os.remove(path)
    utils.save_data(test_data, 'test-save-and-load.csv', "resources")
    data = utils.load_data('test-save-and-load.csv', "resources")

    os.remove(path)

    assert len(data) == 3
    assert data.loc["test"] == [1, 2, 3]