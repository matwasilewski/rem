from typing import Optional, Tuple, Dict

import pandas as pd
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs

from rem.universal import get_soup_from_url
from rem.utils import _extract_divs, _log_wrong_number, _log_unexpected

OTODOM_LINK = "https://www.otodom.pl/"


def otodom_scrap(base_search_url, page_limit=1):
    dataframe = pd.DataFrame()
    generator = otodom_url_generator(base_search_url)

    for url_count, url in enumerate(generator):
        if url_count == page_limit:
            break

        search_soup = get_soup_from_url(url)

        listings_urls = get_all_otodom_listing_urls_for_page(search_soup)
        if len(listings_urls) == 0:
            break

        listing_soups = [get_soup_from_url(url) for url in listings_urls]
        dataframe = extract_data_from_listing_soups(listings_urls)

    return dataframe


def extract_data_from_listing_soups(dataframe, listings):
    for listing in listings:
        listing_data = get_data_from_otodom_listing(listing)
        dataframe = append_new_listing_data(dataframe, listing_data)
    return dataframe


def otodom_url_generator(url):
    parsed_url = urlparse(url)
    page_value = int(parse_qs(parsed_url.query).get("page", [1])[0])
    limit_value = int(parse_qs(parsed_url.query).get("limit", [36])[0])
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    while True:
        yield f"{base_url}?page={page_value}&limit={limit_value}"
        page_value += 1


def get_data_from_otodom_listing(listing):
    listing_data: pd.Series = pd.Series()

    for listing_extractor in LISTING_INFORMATION_RETRIEVAL_FUNCTIONS:
        data = pd.Series(listing_extractor(listing))
        listing_data = listing_data.append(data)

    return listing_data


def append_new_listing_data(dataframe: pd.DataFrame, listing_data: pd.Series):
    new_dataframe = dataframe.append(listing_data, ignore_index=True)
    return new_dataframe


def get_all_otodom_listing_urls_for_page(search_soup):
    lis_standard = get_otodom_standard_listing_urls_for_page(search_soup)
    lis_promoted = get_otodom_promoted_listing_urls_for_page(search_soup)
    if len(lis_standard) == 0:
        return []
    else:
        return lis_promoted + lis_standard


def get_otodom_promoted_listing_urls_for_page(soup: BeautifulSoup):
    promoted_filter = {"data-cy": "search.listing.promoted"}
    promoted_div = soup.find(attrs=promoted_filter)
    lis = promoted_div.findAll("li")
    return get_otodom_listing_urls_from_search_page(lis)


def get_otodom_standard_listing_urls_for_page(soup: BeautifulSoup):
    standard_filter = {"data-cy": "search.listing"}
    divs = soup.find_all(attrs=standard_filter)
    if len(divs) < 2:
        return []
    standard_divs = divs[1]
    lis = standard_divs.findAll("li")
    return get_otodom_listing_urls_from_search_page(lis)


def get_otodom_listing_urls_from_search_page(lis):
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


def get_price(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
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
    return {"price": price}


def get_size(soup: BeautifulSoup) -> Dict[str, Optional[float]]:
    soup_filter = {"aria-label": "Powierzchnia"}

    size_div = _extract_divs(soup, soup_filter, "size")

    if not size_div:
        return {"floor_size_in_m2": None}

    floor_size = []
    for child in size_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Powierzchnia"
        ):
            floor_size = child.contents

    if len(floor_size) != 1:
        _log_wrong_number(len(floor_size), 1, "floor size")
        return {"floor_size_in_m2": None}

    floor_size_float = _resolve_floor_size(floor_size[0])

    return {"floor_size_in_m2": floor_size_float}


def _resolve_floor_size(floor_size: str) -> float:
    floor_size = floor_size.strip()
    floor_size = re.match("^[0-9,.]+", floor_size).group(0)
    floor_size = float(
        re.sub(pattern=",", repl=r".", string=floor_size, flags=re.UNICODE)
    )
    return floor_size


def get_building_type(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    soup_filter = {"aria-label": "Rodzaj zabudowy"}

    type_of_building_div = _extract_divs(soup, soup_filter, "type-of-building")

    if not type_of_building_div:
        return {"building_type": None}

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

    return {"building_type": type_of_building[0][0]}


def get_window_type(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    soup_filter = {"aria-label": "Okna"}

    type_of_window_div = _extract_divs(soup, soup_filter, "window")
    if not type_of_window_div:
        return {"windows_type": None}

    window = []

    for child in type_of_window_div:
        if child.attrs.get("title") is not None and child.attrs.get("title") != "Okna":
            window.append(child.contents)

    if len(window) != 1:
        _log_wrong_number(len(window), 1, "window")
        return None

    return {"windows_type": window[0][0]}


def get_year_of_construction(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
    soup_filter = {"aria-label": "Rok budowy"}

    year_of_construction_div = _extract_divs(soup, soup_filter, "year")
    if not year_of_construction_div:
        return {"year_of_construction": None}

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

    return {"year_of_construction": int(year[0][0])}


def get_number_of_rooms(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
    soup_filter = {"aria-label": "Liczba pokoi"}

    number_of_rooms_div = _extract_divs(soup, soup_filter, "number_of_rooms")
    if not number_of_rooms_div:
        return {"number_of_rooms": None}

    rooms = []

    for child in number_of_rooms_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Liczba pokoi"
        ):
            rooms.append(child.contents)

    if len(rooms) != 1:
        _log_wrong_number(len(rooms), 1, "number_of_rooms")
        return {"number_of_rooms": None}

    return {"number_of_rooms": int(rooms[0][0])}


def get_condition(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    soup_filter = {"aria-label": "Stan wykończenia"}

    condition_div = _extract_divs(soup, soup_filter, "condition")
    if not condition_div:
        return {"condition": None}

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

    return {"condition": condition[0][0]}


def _resolve_floor(floor_string: str) -> Tuple[int, Optional[int]]:
    floor: int
    floors_in_building: Optional[int]
    floor_string = "".join(floor_string.split()).lower()

    if "\\" in floor_string or "/" in floor_string:
        temp_floor, temp_floors_in_building = floor_string.split("/")
        if temp_floor == "parter":
            floor = 0
            floors_in_building = (
                int(temp_floors_in_building) if temp_floors_in_building else None
            )
        else:
            floor = int(temp_floor)
            floors_in_building = (
                int(temp_floors_in_building) if temp_floors_in_building else None
            )
    elif floor_string == "parter":
        floor = 0
        floors_in_building = None
    else:
        floor = int(floor_string)
        floors_in_building = None

    return floor, floors_in_building


def get_total_floors_in_building(soup: BeautifulSoup):
    soup_filter = {"aria-label": "Liczba pięter"}

    floors_in_building_div = _extract_divs(soup, soup_filter, "floors_in_building")
    if not floors_in_building_div:
        return {"floors_in_building": None}

    floors_in_building = []

    for child in floors_in_building_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Liczba pięter"
        ):
            floors_in_building.append(child.contents)

    if len(floors_in_building) != 1:
        _log_wrong_number(len(floors_in_building), 1, "floors_in_building")
        return None

    return {"floors_in_building": int(floors_in_building[0][0])}


def get_floor(soup: BeautifulSoup):
    soup_filter = {"aria-label": "Piętro"}

    floor_div = _extract_divs(soup, soup_filter, "floor")
    if not floor_div:
        return {"floor": None}

    floor_list = []

    for child in floor_div:
        if (
            child.attrs.get("title") is not None
            and child.attrs.get("title") != "Piętro"
        ):
            floor_list.append(child.contents)

    if len(floor_list) != 1:
        _log_wrong_number(len(floor_list), 1, "floor")
        return None

    floor, floors_in_building = _resolve_floor(floor_list[0][0])
    if floors_in_building is None:
        floors_in_building = get_total_floors_in_building(soup)

    return {
        "floor": floor,
        "floors_in_building": floors_in_building["floors_in_building"],
    }


LISTING_INFORMATION_RETRIEVAL_FUNCTIONS = [
    get_price,
    get_size,
    get_building_type,
    get_window_type,
    get_year_of_construction,
    get_number_of_rooms,
    get_condition,
]
