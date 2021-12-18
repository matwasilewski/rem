import os

import pandas as pd
import pytest
from bs4 import BeautifulSoup

from rem.config import settings

import rem.universal
from rem.otodom import Otodom

@pytest.fixture(scope="session", autouse=True)
def otodom_settings() -> Otodom:
    my_settings = settings
    my_settings.BASE_SEARCH_URL = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
    return my_settings

@pytest.fixture(scope="session", autouse=True)
def otodom_instance(otodom_settings) -> Otodom:
    otodom = Otodom(otodom_settings)
    return otodom


@pytest.fixture(scope="session", autouse=False)
def listing() -> BeautifulSoup:
    path = os.sep.join(
        [
            "tests",
            "resources",
            "mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html",
        ]
    )
    with open(path, encoding="utf-8") as fp:
        soup = rem.universal.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=False)
def alternative_listing() -> BeautifulSoup:
    path = os.sep.join(
        ["tests", "resources", "mieszkanie-12-min-do-centrum.html"]
    )
    with open(path, encoding="utf-8") as fp:
        soup = rem.universal.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=False)
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
    example_page = rem.universal.get_website("https://example.com/")
    assert example_page.status_code == 200


def test_get_html_doc() -> None:
    example_page = rem.universal.get_website("https://example.com/")
    example_html = rem.universal.get_html_doc(example_page)
    assert "Example Domain" in example_html


def test_get_soup_from_url() -> None:
    example_page = rem.universal.get_website("https://example.com/")
    example_html = rem.universal.get_html_doc(example_page)
    example_soup = rem.universal.get_soup(example_html)
    assert example_soup.find("h1").text == "Example Domain"


def test_get_soup_from_url_function() -> None:
    example_soup = rem.universal.get_soup_from_url("https://example.com/")
    assert example_soup.find("h1").text == "Example Domain"


def test_load_html(otodom_instance, listing) -> None:
    assert len(listing.contents) == 2


def test_get_price(otodom_instance, listing) -> None:
    price = otodom_instance.get_price(listing)
    assert price == {"price": 1500000}


def test_get_size(otodom_instance, listing) -> None:
    size = otodom_instance.get_size(listing)
    assert size == {"floor_size_in_m2": float(72)}


def test_resolve_floor_size_1(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("72")
    assert size == float(72)


def test_resolve_floor_size_2(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119,64")
    assert size == float(119.64)


def test_resolve_floor_size_3(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119.64")
    assert size == float(119.64)


def test_resolve_floor_size_4(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119")
    assert size == float(119)


def test_resolve_floor_size_5(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119.64m2")
    assert size == float(119.64)


def test_resolve_floor_size_6(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119.64 m2")
    assert size == float(119.64)


def test_resolve_floor_size_7(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119,64 m2")
    assert size == float(119.64)


def test_resolve_floor_size_8(otodom_instance) -> None:
    size = otodom_instance._resolve_floor_size("119,64 m")
    assert size == float(119.64)


def test_type_of_building(otodom_instance, listing) -> None:
    building_type = otodom_instance.get_building_type(listing)
    assert building_type == {"building_type": "kamienica"}


def test_type_of_window(otodom_instance, listing) -> None:
    window_type = otodom_instance.get_window_type(listing)
    assert window_type == {"windows_type": "plastikowe"}


def test_year_of_construction(otodom_instance, listing) -> None:
    year_of_construction = otodom_instance.get_year_of_construction(listing)
    assert year_of_construction == {"year_of_construction": 1939}


def test_number_of_rooms(otodom_instance, listing) -> None:
    number_of_rooms = otodom_instance.get_number_of_rooms(listing)
    assert number_of_rooms == {"number_of_rooms": 3}


def test_condition(otodom_instance, listing) -> None:
    condition = otodom_instance.get_condition(listing)
    assert condition == {"condition": "do zamieszkania"}


def test_floor(otodom_instance, listing) -> None:
    floors = otodom_instance.get_floor(listing)
    assert floors == {"floor": 1, "floors_in_building": 3}


def test_resolve_floor_1(otodom_instance) -> None:
    floor, floors_in_building = otodom_instance._resolve_floor("1/3")
    assert floor == 1
    assert floors_in_building == 3


def test_resolve_floor_2(otodom_instance) -> None:
    floor, floors_in_building = otodom_instance._resolve_floor("Parter")
    assert floor == 0
    assert floors_in_building is None


def test_resolve_floor_3(otodom_instance) -> None:
    floor, floors_in_building = otodom_instance._resolve_floor("Parter / 5")
    assert floor == 0
    assert floors_in_building == 5


def test_resolve_floor_4(otodom_instance) -> None:
    floor, floors_in_building = otodom_instance._resolve_floor("4")
    assert floor == 4
    assert floors_in_building is None


def test_monthly_fee(otodom_instance, listing) -> None:
    monthly_fee = otodom_instance.get_monthly_fee(listing)
    assert monthly_fee == {"monthly_fee": 800}


def test_resolve_monthly_fee_1(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800 zł")
    assert monthly_fee == 800


def test_resolve_monthly_fee_2(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800 ZŁ")
    assert monthly_fee == 800


def test_resolve_monthly_fee_3(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800 PLN")
    assert monthly_fee == 800


def test_resolve_monthly_fee_4(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800,00 zł")
    assert monthly_fee == 800


def test_resolve_monthly_fee_5(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800.00 zł")
    assert monthly_fee == 800


def test_get_listing_url(otodom_instance, listing) -> None:
    listing_url = otodom_instance.get_listing_url(listing)
    assert (
        listing_url["url"]
        == "https://www.otodom.pl/pl/oferta/mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html"
    )


def test_unique_id(otodom_instance, listing) -> None:
    unique_id = otodom_instance.get_unique_id(listing)
    assert unique_id == {"unique_id": 62365446}


def test_ownership_form(otodom_instance, listing) -> None:
    ownership_form = otodom_instance.get_ownership_form(listing)
    assert ownership_form == {"ownership_form": "pełna własność"}


def test_market_type(otodom_instance, listing) -> None:
    market_type = otodom_instance.get_market_type(listing)
    assert market_type == {"market_type": "wtórny"}


def test_construction_material(otodom_instance, listing) -> None:
    construction_material = otodom_instance.get_construction_material(listing)
    assert construction_material == {"construction_material": "cegła"}


@pytest.mark.skip
def test_resolve_outdoor_space_1(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "ogród, taras"
    )
    assert garden == 1
    assert balcony == 0
    assert terrace == 1


@pytest.mark.skip
def test_resolve_outdoor_space_2(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "taras, ogródek"
    )
    assert garden == 1
    assert balcony == 0
    assert terrace == 1


@pytest.mark.skip
def test_resolve_outdoor_space_3(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "balkon, ogródek, taras"
    )
    assert balcony == 1
    assert garden == 1
    assert terrace == 1


@pytest.mark.skip
def test_resolve_outdoor_space_4(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "balkon/ ogródek/ taras"
    )
    assert balcony == 1
    assert garden == 1
    assert terrace == 1


@pytest.mark.skip
def test_resolve_outdoor_space_5(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space("taras")
    assert balcony == 0
    assert garden == 0
    assert terrace == 1


@pytest.mark.skip
def test_resolve_outdoor_space_6(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space("ogródek")
    assert balcony == 0
    assert garden == 1
    assert terrace == 0


@pytest.mark.skip
def test_resolve_outdoor_space_7(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space("ogród")
    assert balcony == 0
    assert garden == 1
    assert terrace == 0


@pytest.mark.skip
def test_resolve_outdoor_space_8(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space("balkon")
    assert balcony == 1
    assert garden == 0
    assert terrace == 0


@pytest.mark.skip
def test_resolve_outdoor_space_9(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "ogródek, balkon"
    )
    assert balcony == 1
    assert garden == 1
    assert terrace == 0


@pytest.mark.skip
def test_resolve_outdoor_space_10(otodom_instance) -> None:
    garden, balcony, terrace = otodom_instance.resolve_outdoor_space(
        "balkon\ taras"
    )
    assert balcony == 1
    assert garden == 0
    assert terrace == 1


@pytest.mark.skip
def test_outdoor_space(otodom_instance, listing) -> None:
    outdoor_space = otodom_instance.get_outdoor_space(listing)
    assert outdoor_space == {"balcony": 1, "garden": 0, "terrace": 0}


def test_heating(otodom_instance, listing) -> None:
    heating = otodom_instance.get_heating(listing)
    assert heating == {"heating": "miejskie"}


def test_address(otodom_instance, listing) -> None:
    address = otodom_instance.get_address(listing)
    assert address == {"address": "Warszawa, Śródmieście, Belwederska"}


def test_get_promoted_listing_urls_for_search_page(
    otodom_instance, search_soup
) -> None:
    promoted_urls = otodom_instance.get_promoted_listing_urls_for_page(
        search_soup
    )
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


def test_get_standard_listintg_urls_for_search_page(
    otodom_instance, search_soup
) -> None:
    standard_urls = otodom_instance.get_standard_listing_urls_for_page(
        search_soup
    )
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


def test_get_all_listings_for_search_page(
    otodom_instance, search_soup
) -> None:
    urls = otodom_instance.get_all_relevant_listing_urls_for_page(search_soup)
    assert len(urls) == 39


def test_get_empty_list_of_urls_for_empty_page(
    otodom_instance, empty_search_soup
) -> None:
    urls = otodom_instance.get_all_relevant_listing_urls_for_page(
        empty_search_soup
    )
    assert len(urls) == 0


def test_url_generator(otodom_instance):
    otodom_instance.base_search_url = (
        "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
    )
    url_generator = otodom_instance.url_generator()

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


def test_url_generator_with_query_parameters(otodom_instance):
    otodom_instance.base_search_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"

    url_generator = otodom_instance.url_generator()
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


def test_get_data_from_listing(otodom_instance, listing) -> None:
    listing_data = otodom_instance.get_data_from_listing(listing)

    assert isinstance(listing_data, pd.Series)
    assert listing_data.loc["price"] == 1500000
    assert listing_data.loc["floor_size_in_m2"] == float(72)
    assert listing_data.loc["building_type"] == "kamienica"
    assert listing_data.loc["windows_type"] == "plastikowe"
    assert listing_data.loc["year_of_construction"] == 1939
    assert listing_data.loc["number_of_rooms"] == 3
    assert listing_data.loc["condition"] == "do zamieszkania"


def test_update_listing_data(
    otodom_instance, listing: BeautifulSoup, alternative_listing: BeautifulSoup
) -> None:
    listing_soups = [listing, alternative_listing]
    otodom_instance.process_listing_soups(listing_soups)

    listing_data = otodom_instance.data
    assert isinstance(listing_data, pd.DataFrame)
    assert len(listing_data.index) == 2
    assert listing_data.loc[0, "price"] == 1500000.0
    assert listing_data.loc[1, "price"] == 1782636.0
    assert listing_data.loc[0, "year_of_construction"] == 1939
    assert listing_data.loc[1, "year_of_construction"] is None


def test_old_and_new_url(otodom_instance) -> None:
    otodom_instance.data = pd.DataFrame(data={"url": ["sample.com"]})
    test_url_not_in_data = "not-in-db.com"
    test_url_in_data = "sample.com"

    assert otodom_instance.is_url_new(test_url_in_data) == False
    assert otodom_instance.is_url_new(test_url_not_in_data) == True


def test_main_page_not_scraped(otodom_instance, search_soup) -> None:
    relevant_listings = otodom_instance.get_all_relevant_listing_urls_for_page(
        search_soup
    )
    assert (
        "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
        not in relevant_listings
    )


@pytest.mark.skip
def test_scrap(otodom_instance):
    otodom_instance.base_search_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
    scrapped_data = otodom_instance.scrap()
    assert isinstance(scrapped_data, pd.DataFrame)
    assert len(scrapped_data.index) == 75
