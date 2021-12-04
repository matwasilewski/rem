import os

import pandas as pd
import pytest
from bs4 import BeautifulSoup

import rem.universal
from rem import otodom
from rem.universal import get_website


@pytest.fixture(scope="session", autouse=True)
def listing_soup() -> BeautifulSoup:
    path = os.sep.join(
        ["tests", "resources", "mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html"]
    )
    with open(path, encoding="utf-8") as fp:
        soup = rem.universal.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=True)
def search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "warszawa-page-1.html"])
    with open(path, encoding="utf-8") as fp:
        soup = rem.universal.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=True)
def empty_search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "warszawa-page-2000.html"])
    with open(path, encoding="utf-8") as fp:
        soup = rem.universal.get_soup(fp)
    return soup


def test_get_website() -> None:
    example_page = rem.universal.get_website("http://example.com/")
    assert example_page.status_code == 200


def test_get_html_doc() -> None:
    example_page = rem.universal.get_website("http://example.com/")
    example_html = rem.universal.get_html_doc(example_page)
    assert "Example Domain" in example_html


def test_get_soup_from_url() -> None:
    example_page = rem.universal.get_website("http://example.com/")
    example_html = rem.universal.get_html_doc(example_page)
    example_soup = rem.universal.get_soup(example_html)
    assert example_soup.find("h1").text == "Example Domain"


def test_get_soup_from_url_function() -> None:
    example_soup = rem.universal.get_soup_from_url("http://example.com/")
    assert example_soup.find("h1").text == "Example Domain"


def test_load_html(listing_soup) -> None:
    assert len(listing_soup.contents) == 2


def test_get_price(listing_soup) -> None:
    price = otodom.get_price(listing_soup)
    assert price == {"price": 1500000}


def test_get_size(listing_soup) -> None:
    size = otodom.get_size(listing_soup)
    assert size == {"floor_size_in_m2": float(72)}


def test_type_of_building(listing_soup) -> None:
    building_type = otodom.get_building_type(listing_soup)
    assert building_type == {"building_type": "kamienica"}


def test_type_of_window(listing_soup) -> None:
    window_type = otodom.get_window_type(listing_soup)
    assert window_type == {"windows_type": "plastikowe"}


def test_year_of_construction(listing_soup) -> None:
    year_of_construction = otodom.get_year_of_construction(listing_soup)
    assert year_of_construction == {"year_of_construction": 1939}


def test_number_of_rooms(listing_soup) -> None:
    number_of_rooms = otodom.get_number_of_rooms(listing_soup)
    assert number_of_rooms == {"number_of_rooms": 3}


def test_condition(listing_soup) -> None:
    condition = otodom.get_condition(listing_soup)
    assert condition == {"condition": "do zamieszkania"}


def test_floor(listing_soup) -> None:
    floors = otodom.get_floor(listing_soup)
    assert floors == {"floor": 1, "floors_in_building": 3}


def test_resolve_floor_1() -> None:
    floor, floors_in_building = otodom._resolve_floor("1/3")
    assert floor == 1
    assert floors_in_building == 3


def test_resolve_floor_2() -> None:
    floor, floors_in_building = otodom._resolve_floor("Parter")
    assert floor == 0
    assert floors_in_building is None


def test_resolve_floor_3() -> None:
    floor, floors_in_building = otodom._resolve_floor("Parter / 5")
    assert floor == 0
    assert floors_in_building == 5


def test_resolve_floor_4() -> None:
    floor, floors_in_building = otodom._resolve_floor("4")
    assert floor == 4
    assert floors_in_building is None


def test_get_promoted_listing_urls_for_search_page(search_soup) -> None:
    promoted_urls = otodom.get_otodom_promoted_listing_urls_for_page(search_soup)
    assert len(promoted_urls) == 3
    assert (
        promoted_urls[0] == "https://www.otodom.pl/pl/oferta/nowa"
        "-kawalerka-odbior-kluczy-1q2022-ochota-wloch"
        "-ID4blGn"
    )
    assert (
        promoted_urls[1] == "https://www.otodom.pl/pl/oferta/apartament"
        "-130-m-w-babka-tower-ID4ehmq"
    )
    assert (
        promoted_urls[2] == "https://www.otodom.pl/pl/oferta/penthouse-na"
        "-marymonckiej-ID4ehkP"
    )


def test_get_standard_listintg_urls_for_search_page(search_soup) -> None:
    standard_urls = otodom.get_otodom_standard_listing_urls_for_page(search_soup)
    assert len(standard_urls) == 36
    assert (
        standard_urls[0] == "https://www.otodom.pl/pl/oferta/kawalerka"
        "-warszawa-ul-fundamentowa-ID47bq4"
    )
    assert (
        standard_urls[1] == "https://www.otodom.pl/pl/oferta/mieszkanie"
        "-dla-rodziny-przy-parku-szczesliwickim"
        "-ID4dVV3"
    )
    assert (
        standard_urls[-2] == "https://www.otodom.pl/pl/oferta/dwupokojowe"
        "-nowe-i-do-odbioru-ID4ebFQ"
    )
    assert (
        standard_urls[-1] == "https://www.otodom.pl/pl/oferta/z-tarasem"
        "-18-52m2-10min-do-centrum-blisko-skm-ID4enyi"
    )


def test_get_all_listings_for_search_page(search_soup) -> None:
    urls = otodom.get_all_otodom_listings_for_page(search_soup)
    assert len(urls) == 39


def test_get_empty_list_of_urls_for_empty_page(empty_search_soup) -> None:
    urls = otodom.get_all_otodom_listings_for_page(empty_search_soup)
    assert len(urls) == 0


def test_url_generator():
    url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
    url_generator = otodom.otodom_url_generator(url)

    assert (
        next(url_generator) == "https://www.otodom.pl/pl/oferty/sprzedaz"
        "/mieszkanie/warszawa?page=1&limit=36"
    )
    assert (
        next(url_generator)
        == "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
        "?page=2&limit=36"
    )
    assert (
        next(url_generator)
        == "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
        "?page=3&limit=36"
    )


def test_url_generator_with_query_parameters():
    url = (
        "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page"
        "=1&limit=72"
    )
    url_generator = otodom.otodom_url_generator(url)
    assert (
        next(url_generator) == "https://www.otodom.pl/pl/oferty/sprzedaz"
        "/mieszkanie/warszawa?page=1&limit=72"
    )
    assert (
        next(url_generator) == "https://www.otodom.pl/pl/oferty/sprzedaz"
        "/mieszkanie/warszawa?page=2&limit=72"
    )
    assert (
        next(url_generator) == "https://www.otodom.pl/pl/oferty/sprzedaz"
        "/mieszkanie/warszawa?page=3&limit=72"
    )


@pytest.mark.skip
def test_scrap():
    url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
    scrapped_data = otodom.otodom_scrap(url)
    assert isinstance(scrapped_data, pd.DataFrame)
    assert len(scrapped_data.index) == 75


@pytest.mark.skip
def test_unique_id(listing_soup) -> None:
    unique_id = otodom.get_unique_id(
        listing_soup,
    )
    assert unique_id == 62365446
