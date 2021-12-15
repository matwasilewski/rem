import os

import pandas as pd

from rem import utils


def test_load_data() -> None:
    dir_path = os.sep.join(["tests", "resources"])
    loaded_data = utils.load_data('warszawa-sprzedaz.csv', dir_path)
    assert isinstance(loaded_data, pd.DataFrame)


def test_save_data() -> None:
    test_data = pd.DataFrame({"test": [1, 2, 3]})
    path = os.sep.join(["tests", "resources", "test-save-and-load.csv"])
    dir_path = os.sep.join(["tests", "resources"])

    if os.path.exists(path):
        os.remove(path)

    utils.save_data(test_data, 'test-save-and-load', dir_path)
    data = utils.load_data('test-save-and-load', dir_path)

    os.remove(path)

    assert len(data) == 3
    assert data.test[0] == 1
    assert data.test[1] == 2
    assert data.test[2] == 3
