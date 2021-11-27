import os

import pytest
from bs4 import BeautifulSoup

import otodom


@pytest.fixture(scope='session', autouse=True)
def listing_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html"])
    with open(path, encoding="utf-8") as fp:
        soup = otodom.get_soup(fp)
    return soup


@pytest.fixture(scope='session', autouse=True)
def search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "www.otodom.pl", "pl", "oferty", "sprzedaz",
                        "mieszkanie", "warszawa?page=1.html"])
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


def test_get_promoted_urls_for_page(search_soup) -> None:
    promoted_urls = otodom.get_promoted_urls_for_page(search_soup)
    assert len(promoted_urls) == 3
