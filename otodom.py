from typing import Union, TextIO, Optional
import logging
from bs4 import BeautifulSoup
import re


def get_listing(path: Union[str, TextIO]):
    soup = BeautifulSoup(path, "html.parser")
    return soup


def get_price(soup: BeautifulSoup) -> Optional[int]:
    soup_filter = {"aria-label": "Cena"}

    price_div = _extract_divs(soup, soup_filter, "price")

    if len(price_div) != 1:
        _log_wrong_number(len(price_div), 1, "price")

    if "." in price_div[0]:
        _log_unexpected(".", "price")
    elif "," in price_div[0]:
        _log_unexpected(",", "price")

    price = int(re.sub(pattern=r'[^0-9,.]',
                       repl=u'',
                       string=price_div[0],
                       flags=re.UNICODE))
    return price


def get_size(soup: BeautifulSoup) -> Optional[float]:
    soup_filter = {"aria-label": "Powierzchnia"}

    size_div = _extract_divs(soup, soup_filter, "size")

    if not size_div:
        return None

    floor_size = []
    for child in size_div:
        if child.attrs.get("title") is not None and child.attrs.get(
                "title") != "Powierzchnia":
            floor_size = child.contents

    if len(floor_size) != 1:
        _log_wrong_number(len(floor_size), 1, "floor size")
        return None

    floor_size_float = float(re.sub(pattern=r'[^0-9,.]',
                                    repl=u'',
                                    string=floor_size[0],
                                    flags=re.UNICODE))

    return floor_size_float


def get_building_type(soup):
    soup_filter = {"aria-label": "Rodzaj zabudowy"}

    type_of_building_div = _extract_divs(soup, soup_filter, "type-of-building")

    if not type_of_building_div:
        return None

    rodzaj = []

    for child in type_of_building_div:
        if child.attrs.get("title") is not None and child.attrs.get(
                "title") != "Rodzaj zabudowy":
            rodzaj.append(child.contents)

    if len(rodzaj) != 1:
        _log_wrong_number(len(rodzaj), 1, "type of building")
        return None

    return rodzaj[0][0]


def get_window_type(soup):
    soup_filter = {"aria-label": "Okna"}

    type_of_window_div = _extract_divs(soup, soup_filter, "window")
    if not type_of_window_div:
        return None

    window = []

    for child in type_of_window_div:
        if child.attrs.get("title") is not None and child.attrs.get(
                "title") != "Okna":
            window.append(child.contents)

    if len(window) != 1:
        _log_wrong_number(len(window), 1, "window")
        return None

    return window[0][0]


def get_year_of_construction(soup):
    soup_filter = {"aria-label": "Rok budowy"}

    year_of_construction_div = _extract_divs(soup, soup_filter, "year")
    if not year_of_construction_div:
        return None

    year = []

    for child in year_of_construction_div:
        if child.attrs.get("title") is not None and child.attrs.get(
                "title") != "Rok budowy":
            year.append(child.contents)

    if len(year) != 1:
        _log_wrong_number(len(year), 1, "year")
        return None

    return int(year[0][0])


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
    logging.error(f"{actual} {what} found for the listing, "
                  f"instead of expected {expected}. Skipping the record.")


def _log_unexpected(unexpected: str, where: str) -> None:
    logging.error(f"Unexpected {unexpected} encountered in {where} "
                  f"in the listing")
