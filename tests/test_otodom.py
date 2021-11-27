import os

import pytest
from bs4 import BeautifulSoup

import otodom


@pytest.fixture(scope='session', autouse=True)
def listing_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources",
                        "mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html"])
    with open(path, encoding="utf-8") as fp:
        soup = otodom.get_soup(fp)
    return soup


@pytest.fixture(scope='session', autouse=True)
def search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "www.otodom.pl", "pl", "oferty",
                        "sprzedaz", "mieszkanie", "warszawa?page=1.html"])
    with open(path, encoding="utf-8") as fp:
        soup = otodom.get_soup(fp)
    return soup


def test_load_html(listing_soup) -> None:
    assert len(listing_soup.contents) == 2


def test_get_price(listing_soup) -> None:
    price = otodom.get_price(listing_soup)
    assert price == 1500000


def test_get_size(listing_soup) -> None:
    size = otodom.get_size(listing_soup)
    assert size == float(72)


def test_type_of_building(listing_soup) -> None:
    building_type = otodom.get_building_type(listing_soup)
    assert building_type == "kamienica"


def test_type_of_window(listing_soup) -> None:
    window_type = otodom.get_window_type(listing_soup)
    assert window_type == "plastikowe"


def test_year_of_construction(listing_soup) -> None:
    year_of_construction = otodom.get_year_of_construction(listing_soup)
    assert year_of_construction == 1939


def test_get_promoted_listing_urls_for_search_page(search_soup) -> None:
    promoted_urls = otodom.get_promoted_listing_urls_for_page(search_soup)
    assert len(promoted_urls) == 3
    assert promoted_urls[0] == 'https://www.otodom.pl/pl/oferta/nowa' \
                               '-kawalerka-odbior-kluczy-1q2022-ochota-wloch' \
                               '-ID4blGn'
    assert promoted_urls[1] == 'https://www.otodom.pl/pl/oferta/apartament' \
                               '-130-m-w-babka-tower-ID4ehmq'
    assert promoted_urls[2] == 'https://www.otodom.pl/pl/oferta/penthouse-na' \
                               '-marymonckiej-ID4ehkP'


def test_get_standard_listintg_urls_for_search_page(search_soup) -> None:
    standard_urls = otodom.get_standard_listing_urls_for_page(search_soup)
    assert len(standard_urls) == 36


def test_get_all_listings_for_search_page(search_soup) -> None:
    urls = otodom.get_all_listings_for_page(search_soup)
    assert len(urls) == 39
