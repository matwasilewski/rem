from typing import Union, TextIO, Optional, Tuple
import logging

import pandas as pd
from bs4 import BeautifulSoup
import re
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs

from requests import Request, Response

OTODOM_LINK = "https://www.otodom.pl/"


def get_all_listings_for_page(search_soup):
    lis_standard = get_standard_listing_urls_for_page(search_soup)
    lis_promoted = get_promoted_listing_urls_for_page(search_soup)
    if len(lis_standard) == 0:
        return []
    else:
        return lis_promoted + lis_standard


def get_promoted_listing_urls_for_page(soup):
    promoted_filter = {"data-cy": "search.listing.promoted"}
    promoted_div = soup.find(attrs=promoted_filter)
    lis = promoted_div.findAll("li")
    return _get_listing_urls_for_page(lis)


def get_standard_listing_urls_for_page(soup):
    standard_filter = {"data-cy": "search.listing"}
    divs = soup.find_all(attrs=standard_filter)
    if len(divs) < 2:
        return []
    standard_divs = divs[1]
    lis = standard_divs.findAll("li")
    return _get_listing_urls_for_page(lis)


def _get_listing_urls_for_page(lis):
    links = []
    for li in lis:
        local_links = []
        for element in li:
            if element.has_attr("href"):
                local_links.append(element["href"])
        if len(local_links) == 1:
            links.append(local_links[0])
        else:
            _log_wrong_number(len(local_links), 1, "listing links")
    return links


def get_website(url: str) -> Response:
    page = requests.get(url)
    return page


def get_html_doc(response):
    page = response.text
    return page


def get_soup(html_doc: TextIO):
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def get_soup_from_url(url):
    page = get_website(url)
    html = get_html_doc(page)
    soup = get_soup(html)
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

    price = int(
        re.sub(pattern=r"[^0-9,.]", repl="", string=price_div[0], flags=re.UNICODE)
    )
    return price


def get_size(soup: BeautifulSoup) -> Optional[float]:
    soup_filter = {"aria-label": "Powierzchnia"}

    size_div = _extract_divs(soup, soup_filter, "size")

    if not size_div:
        return None

    floor_size = []
    for child in size_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Powierzchnia"
        ):
            floor_size = child.contents

    if len(floor_size) != 1:
        _log_wrong_number(len(floor_size), 1, "floor size")
        return None

    floor_size_float = float(
        re.sub(pattern=r"[^0-9,.]", repl="", string=floor_size[0], flags=re.UNICODE)
    )

    return floor_size_float


def get_building_type(soup):
    soup_filter = {"aria-label": "Rodzaj zabudowy"}

    type_of_building_div = _extract_divs(soup, soup_filter, "type-of-building")

    if not type_of_building_div:
        return None

    type_of_building = []

    for child in type_of_building_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Rodzaj zabudowy"
        ):
            type_of_building.append(child.contents)

    if len(type_of_building) != 1:
        _log_wrong_number(len(type_of_building), 1, "type of building")
        return None

    return type_of_building[0][0]


def get_window_type(soup):
    soup_filter = {"aria-label": "Okna"}

    type_of_window_div = _extract_divs(soup, soup_filter, "window")
    if not type_of_window_div:
        return None

    window = []

    for child in type_of_window_div:
        if child.attrs.get("title") is not None and child.attrs.get("title") != "Okna":
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
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Rok budowy"
        ):
            year.append(child.contents)

    if len(year) != 1:
        _log_wrong_number(len(year), 1, "year")
        return None

    return int(year[0][0])

def get_number_of_rooms(soup):
    soup_filter = {"aria-label": "Liczba pokoi"}

    number_of_rooms_div = _extract_divs(soup, soup_filter, "number_of_rooms")
    if not number_of_rooms_div:
        return None

    rooms = []

    for child in number_of_rooms_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Liczba pokoi"
        ):
            rooms.append(child.contents)

    if len(rooms) != 1:
        _log_wrong_number(len(rooms), 1, "number_of_rooms")
        return None

    return int(rooms[0][0])

def get_condition(soup):
    soup_filter = {"aria-label": "Stan wykończenia"}

    condition_div = _extract_divs(soup, soup_filter, "condition")
    if not condition_div:

        return None

    condition = []

    for child in condition_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Stan wykończenia"
        ):
            condition.append(child.contents)

    if len(condition) != 1:
        _log_wrong_number(len(condition), 1, "condition")
        return None

    return condition[0][0]


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
    logging.error(f"Unexpected {unexpected} encountered in {where} in the listing")


LISTING_INFORMATION_RETRIEVAL_FUNCTIONS = [
    get_price,
    get_size,
    get_building_type,
    get_window_type,
    get_year_of_construction,
]


def scrap(base_search_url):
    generator = get_url_generator(base_search_url)
    scrapped_data = pd.DataFrame()

    for url in generator:
        search_soup = get_soup_from_url(url)
        listings = get_all_listings_for_page(search_soup)
        if len(listings) == 0:
            break
        for listing in listings:
            listing_data = get_data_from_listing(listing)
            update_listing_data(scrapped_data, listing_data)
    return scrapped_data


def get_url_generator(url):
    parsed_url = urlparse(url)
    page_value = int(parse_qs(parsed_url.query).get("page", [1])[0])
    limit_value = int(parse_qs(parsed_url.query).get("limit", [36])[0])
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    while True:
        yield f"{base_url}?page={page_value}&limit={limit_value}"
        page_value += 1


def get_data_from_listing(listing):
    return pd.DataFrame()


def update_listing_data(scrapped_data: pd.DataFrame, listing_data: pd.DataFrame):
    pass


def resolve_floor(floor_string: str) -> Tuple[int, Optional[int]]:
    floor: int
    floors_in_building: Optional[int]
    floor_string = "".join(floor_string.split()).lower()

    if "\\" in floor_string or "/" in floor_string:
        temp_floor, temp_floors_in_building = floor_string.split("/")
        if temp_floor == "parter":
            floor=0
            floors_in_building = int(temp_floors_in_building) if temp_floors_in_building else None
        else:
            floor = int(temp_floor)
            floors_in_building = int(temp_floors_in_building) if temp_floors_in_building else None
    elif floor_string == "parter":
        floor = 0
        floors_in_building = None
    else:
        floor = int(floor_string)
        floors_in_building = None

    return floor, floors_in_building

def get_floor(listing_soup):
    floor, floors_in_building = resolve_floor(floor_string)

    return None