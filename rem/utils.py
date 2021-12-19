import os.path
import time
from typing import TextIO

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import Response

from rem.logger import log


def _extract_divs(soup, soup_filter, what: str):
    divs = soup.find_all(attrs=soup_filter)

    if len(divs) > 1:
        log_wrong_number(len(divs), 1, what)
        return None
    elif len(divs) == 0:
        log_wrong_number(0, 1, what)
        return None
    nested_div = list(divs[0].children)

    return nested_div


def log_wrong_number(actual: int, expected: int, what: str) -> None:
    log.error(
        f"{actual} {what} found for the listing, "
        f"instead of expected {expected}."
    )


def log_unexpected(unexpected: str, where: str) -> None:
    log.error(f"Unexpected {unexpected} encountered in {where} in the listing")


def load_data(file_name, data_dir="data"):
    try:
        data_path = os.sep.join([data_dir, f"{file_name}.csv"])
        df = pd.read_csv(data_path)
        log.info(f"Loading existing data containing {len(df)} records...")
        return df
    except FileNotFoundError:
        log.info(f"No existing data found.")
        return pd.DataFrame()


def save_data(data: pd.DataFrame, file_name, data_dir="data"):
    data_path = os.sep.join([data_dir, f"{file_name}.csv"])
    log.info(f"Saving data to {data_path}...")

    if os.path.isfile(data_path):
        log.warning("Overwriting data")

    data.to_csv(data_path)


def get_website(url: str) -> Response:
    page = requests.get(url)
    return page


def get_html_doc(response):
    page = response.text
    return page


def get_soup(html_doc: TextIO):
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def get_soup_from_url(url, offset=0):
    page = get_website(url)
    time.sleep(offset)
    html = get_html_doc(page)
    soup = get_soup(html)
    return soup
