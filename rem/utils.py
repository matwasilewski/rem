import logging
import os.path

import pandas as pd


def _extract_divs(soup, soup_filter, what: str):
    divs = soup.find_all(attrs=soup_filter)

    if len(divs) > 1:
        _log_wrong_number(len(divs), 1, what)
        return None
    elif len(divs) == 0:
        _log_wrong_number(0, 1, what)
        return None
    nested_div = list(divs[0].children)

    return nested_div


def _log_wrong_number(actual: int, expected: int, what: str) -> None:
    logging.error(
        f"{actual} {what} found for the listing, "
        f"instead of expected {expected}. Skipping the record."
    )


def _log_unexpected(unexpected: str, where: str) -> None:
    logging.error(
        f"Unexpected {unexpected} encountered in {where} in the listing"
    )


def load_data(file_name, data_dir="data"):
    try:
        data_path = os.sep.join([data_dir, f"{file_name}.csv"])
        df = pd.read_csv(data_path)
        logging.info(f"Loading existing data containing {len(df)} records...")
        return df
    except FileNotFoundError:
        logging.info(f"No existing data found.")
        return pd.DataFrame()


def save_data(data: pd.DataFrame, file_name, data_dir="data"):
    data_path = os.sep.join([data_dir, f"{file_name}.csv"])
    logging.info(f"Saving data to {data_path}...")

    if os.path.isfile(data_path):
        logging.warning("Overwriting data")

    data.to_csv(data_path)
