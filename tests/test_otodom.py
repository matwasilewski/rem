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
