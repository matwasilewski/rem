import pytest
from bs4 import BeautifulSoup

import otodom


@pytest.fixture(scope='session', autouse=True)
def soup() -> BeautifulSoup:
    path = "tests/resources/mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html"
    with open(path) as fp:
        soup = otodom.get_listing(fp)
    return soup


def test_load_html(soup) -> None:
    assert len(soup.contents) == 2


def test_get_price(soup) -> None:
    price = otodom.get_price(soup)
    assert price == 1500000


def test_get_size(soup) -> None:
    size = otodom.get_size(soup)
    assert size == float(72)


def test_type_of_building(soup) -> None:
    building_type = otodom.get_building_type(soup)
    assert building_type == "kamienica"
