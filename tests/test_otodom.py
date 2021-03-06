import datetime
import os
import re
import time

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from requests_cache import CachedSession

import rem.otodom
import rem.utils
from rem.config import get_settings, Settings

from rem.otodom import Otodom


@pytest.fixture(scope="session")
def test_session() -> CachedSession:
    test_session = CachedSession(
        os.sep.join([".cache", "test_cache"]),
        backend="sqlite",
    )
    return test_session


@pytest.fixture(scope="session", autouse=False)
def otodom_settings() -> Settings:
    my_settings = get_settings()
    my_settings.BASE_SEARCH_URL = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
    my_settings.LOAD_FROM_DATA = False
    my_settings.DOWNLOAD_LISTINGS_ALREADY_IN_FILE = True
    my_settings.OFFSET = 0
    my_settings.PAGE_LIMIT = 1
    my_settings.USE_GOOGLE_MAPS_API = False
    my_settings.DATA_FILE_NAME = "otodom_test"
    my_settings.LOG_DIR = os.sep.join(
        ["logs", f"test-{int(time.time())}-rem.log"]
    )

    yield my_settings


@pytest.fixture(scope="session", autouse=False)
def otodom_instance(otodom_settings) -> Otodom:
    otodom = Otodom(otodom_settings)
    return otodom


@pytest.fixture(scope="session", autouse=False)
def otodom_gcp_settings() -> Settings:
    my_settings = get_settings()
    my_settings.BASE_SEARCH_URL = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
    my_settings.USE_GOOGLE_MAPS_API = True
    return my_settings


@pytest.fixture(scope="session", autouse=False)
def otodom_gcp_instance(otodom_gcp_settings) -> Otodom:
    otodom = Otodom(otodom_gcp_settings)
    return otodom


@pytest.fixture(scope="session", autouse=True)
def listing() -> BeautifulSoup:
    path = os.sep.join(
        [
            "tests",
            "resources",
            "mieszkanie-w-kamienicy-w-srodmiesciu-ID4dG6i.html",
        ]
    )
    with open(path, encoding="utf-8") as fp:
        soup = rem.utils.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=False)
def alternative_listing() -> BeautifulSoup:
    path = os.sep.join(
        ["tests", "resources", "mieszkanie-12-min-do-centrum.html"]
    )
    with open(path, encoding="utf-8") as fp:
        soup = rem.utils.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=False)
def search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "warszawa-page-1.html"])
    with open(path, encoding="utf-8") as fp:
        soup = rem.utils.get_soup(fp)
    return soup


@pytest.fixture(scope="session", autouse=True)
def empty_search_soup() -> BeautifulSoup:
    path = os.sep.join(["tests", "resources", "warszawa-page-2000.html"])
    with open(path, encoding="utf-8") as fp:
        soup = rem.utils.get_soup(fp)
    return soup


def test_get_website(otodom_instance) -> None:
    example_page = otodom_instance.get_website("https://example.com/")
    assert example_page.status_code == 200


def test_get_html_doc(otodom_instance) -> None:
    example_page = otodom_instance.get_website("https://example.com/")
    example_html = rem.utils.get_html_doc(example_page)
    assert "Example Domain" in example_html


def test_get_soup_from_url(otodom_instance) -> None:
    example_page = otodom_instance.get_website("https://example.com/")
    example_html = rem.utils.get_html_doc(example_page)
    example_soup = rem.utils.get_soup(example_html)
    assert example_soup.find("h1").text == "Example Domain"


def test_get_soup_from_url_function(otodom_instance) -> None:
    example_soup = otodom_instance.get_soup_from_url("https://example.com/")
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
    monthly_fee = otodom_instance.resolve_monthly_fee("800 z??")
    assert monthly_fee == 800


def test_resolve_monthly_fee_2(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800 Z??")
    assert monthly_fee == 800


def test_resolve_monthly_fee_3(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800 PLN")
    assert monthly_fee == 800


def test_resolve_monthly_fee_4(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800,00 z??")
    assert monthly_fee == 800


def test_resolve_monthly_fee_5(otodom_instance) -> None:
    monthly_fee = otodom_instance.resolve_monthly_fee("800.00 z??")
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
    assert ownership_form == {"ownership_form": "pe??na w??asno????"}


def test_market_type(otodom_instance, listing) -> None:
    market_type = otodom_instance.get_market_type(listing)
    assert market_type == {"market_type": "wt??rny"}


def test_construction_material(otodom_instance, listing) -> None:
    construction_material = otodom_instance.get_construction_material(listing)
    assert construction_material == {"construction_material": "ceg??a"}


def test_heating(otodom_instance, listing) -> None:
    heating = otodom_instance.get_heating(listing)
    assert heating == {"heating": "miejskie"}


def test_address(otodom_instance, listing) -> None:
    address = otodom_instance.get_address(listing)
    assert address == {"address": "Warszawa, ??r??dmie??cie, Belwederska"}


def test_ad_description(otodom_instance, listing) -> None:
    ad_description = otodom_instance.get_ad_description(listing)
    assert ad_description == {
        "ad_description": "Gratka dla fan??w przedwojennych kamienic! Jeden z najlepszych adres??w w Warszawie! To tylko niekt??re ze zda??, kt??re idealnie opisuj?? t?? nieruchomo????. Mieszkanie zlokalizowane jest przy Trakcie Kr??lewskim, zaledwie 2 minuty spacerem od ??azienek Kr??lewskich w pi??knej, modernistycznej kamienicy z lat 30tych, z zachowanymi przedwojennymi ???smaczkami??? dla koneser??w. PARAMETRY NIERUCHOMO??CIMieszkanie ma bardzo dobry i wygodny rozk??ad. Salon z aneksem kuchennym wychodzi na ulic?? Belwedersk??, roztacza si?? z niego widok na zielony ogr??d Ambasady Rosji. Dwie sypialnie (jedna z balkonem) oraz ??azienka z oknem wychodz?? na ciche, zielone patio. W przedpokoju znajduj?? si?? wbudowane szafy. Pomieszczenia wysokie s?? na 3 metry, zainstalowana klimatyzacja, odrestaurowane oryginalne grzejniki, to tylko kilka z dodatkowych atut??w oferowanej nieruchomo??ci. Kamienica posiada w??asne, zamykane patio z parkingiem tylko dla mieszka??c??w. Do mieszkania przynale??y kom??rka lokatorska o powierzchni 10 m2. KOMUNIKACJA I OKOLICANieruchomo???? le??y na pograniczu ??r??dmie??cia i Mokotowa. W pobli??u przystanki autobusowe, do tramwaju 10 minut piechot??. Od serca Warszawy dziel?? nas 4 kilometry. Do ??azienek Kr??lewskich 2 minuty. W okolicy ambasady, kamienice i du??o zieleni. W NASZEJ OPINIINieruchomo???? jakich ma??o! Przedwojenna, zadbana, modernistyczna kamienica z w??asnym patio i parkingiem, s??siedztwo ??azienek Kr??lewskich oraz wygodny rozk??ad mieszkania zadowoli zar??wno par?? lubi??c?? klimatyczne nieruchomo??ci, rodzin?? 2+1, jak r??wnie?? nadaje si?? do dalszego wynajmu. Wi??cej unikalnych ofert w podobnych kryteriach znajd?? Pa??stwo na naszej stronie . Zapraszamy!A lucky strike for fans of pre-war tenement houses! One of the best addresses in Warsaw! These are just some of the sentences that perfectly describe this property. The apartment is located on the Trakt Kr??lewski, just a 2-minute walk from the Royal ??azienki Park in a beautiful, modernist tenement house from the 1930s, with pre-war \"flavors\" for connoisseurs.PROPERTY PARAMETERSThe apartment has a very good and comfortable layout. The living room with a kitchenette overlooks Belwederska Street and offers a view of the green garden of the Russian Embassy. Two bedrooms (one with a balcony) and a bathroom with a window overlook a quiet, green patio. There are built-in wardrobes in the hall. The rooms are 3 meters high, air conditioning installed, restored original heaters are just a few of the additional advantages of the offered property. The tenement house has its own, closed patio with a parking lot for residents only. The apartment includes a storage room with an area of 10 m2.COMMUNICATION AND SURROUNDINGSThe property is located on the border of ??r??dmie??cie and Mokot??w. Nearby bus stops, 10 minutes on foot to the tram. We are 4 kilometers away from the heart of Warsaw. To the Royal ??azienki 2 minutes. In the neighborhood embassies, tenement houses and lots of greenery.IN OUR OPINIONReal estate like no other! Pre-war, well-kept, modernist tenement house with its own patio and parking, the vicinity of Royal ??azienki Park and a convenient layout of the apartment will satisfy both a couple who like atmospheric real estate, a 2 + 1 family, and is also suitable for further rental.Please visit our website to find more unique offers with similar criteria!"
    }


def test_seller_type(otodom_instance, listing) -> None:
    seller_type = otodom_instance.get_seller_type(listing)
    assert seller_type == {"seller_type": "agency"}


def test_extract_long_lat_via_address(otodom_gcp_instance, listing) -> None:
    coordinates = otodom_gcp_instance.extract_long_lat_via_address(
        "Warszawa, ??r??dmie??cie, Belwederska"
    )

    assert coordinates == {"latitude": 52.2098433, "longitude": 21.028336}


@pytest.mark.skip
def test_get_transit_time_distance(otodom_gcp_instance, listing) -> None:
    distance_time_to_city_center = (
        otodom_gcp_instance.get_transit_time_distance(52.2098433, 21.028336)
    )
    assert distance_time_to_city_center == {
        "distance_to center": "3.5 km",
        "commuting_time_min": "45 mins",
    }


@pytest.mark.skip
def test_get_driving_time_distance(otodom_gcp_instance, listing) -> None:
    distance_time_to_city_center_driving = (
        otodom_gcp_instance.get_driving_time_distance(52.2098433, 21.028336)
    )
    assert distance_time_to_city_center_driving == {
        "driving_distance_to center": "4.2 km",
        "driving_commuting_time_min": "11 mins",
    }


@pytest.mark.skip
def test_get_bicycling_time_distance(otodom_gcp_instance, listing) -> None:
    distance_time_to_city_center_driving = (
        otodom_gcp_instance.get_bicycling_time_distance(52.2098433, 21.028336)
    )
    assert distance_time_to_city_center_driving == {
        "bicycling_distance_to center": "4.1 km",
        "bicycling_commuting_time_min": "15 mins",
    }


@pytest.mark.skip
def test_get_walking_time_distance(otodom_gcp_instance, listing) -> None:
    distance_time_to_city_center_driving = (
        otodom_gcp_instance.get_walking_time_distance(52.2098433, 21.028336)
    )
    assert distance_time_to_city_center_driving == {
        "walking_distance_to center": "3.5 km",
        "walking_commuting_time_min": "45 mins",
    }


def test_resolve_additional_features(otodom_instance, listing) -> None:
    additional_features_list = otodom_instance.resolve_additional_features(
        listing
    )
    assert additional_features_list == {
        'internet',
        'system alarmowy',
        'drzwi / okna antyw??amaniowe',
        "drzwi",
        "okna antyw??amaniowe",
        'teren zamkni??ty',
        'domofon / wideofon',
        "domofon",
        "wideofon",
        'klimatyzacja',
        'balkon',
        'piwnica',
        'gara??/miejsce parkingowe',
        "gara??",
        "miejsce parkingowe",
    }


def test_get_parking_space(otodom_instance, listing) -> None:
    parking_space = otodom_instance.get_parking_space(listing)
    assert parking_space == {"parking": 1, "garage": 1}


def test_get_outdoor_space(otodom_instance, listing) -> None:
    outdoor_space = otodom_instance.get_outdoor_space(listing)
    assert outdoor_space == {"balcony": 1, "garden": 0, "terrace": 0}


def test_get_elevator(otodom_instance, listing) -> None:
    elevator = otodom_instance.get_elevator(listing)
    assert elevator == {"elevator": 0}


def test_get_air_conditioning(otodom_instance, listing) -> None:
    air_conditioning = otodom_instance.get_air_conditioning(listing)
    assert air_conditioning == {"air_conditioning": 1}


def test_get_basement(otodom_instance, listing) -> None:
    basement = otodom_instance.get_basement(listing)
    assert basement == {"basement": 1}


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
    urls, metadata = otodom_instance.get_all_relevant_listing_urls_for_page(
        search_soup
    )
    assert len(urls) == 39


def test_get_empty_list_of_urls_for_empty_page(
    otodom_instance, empty_search_soup
) -> None:
    urls, metadata = otodom_instance.get_all_relevant_listing_urls_for_page(
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
    (
        relevant_listings,
        metadata,
    ) = otodom_instance.get_all_relevant_listing_urls_for_page(search_soup)
    assert (
        "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa"
        not in relevant_listings
    )


def test_creation_date(otodom_instance, listing) -> None:
    time = otodom_instance.get_creation_time(listing)
    assert re.match(
        r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})", time["created_at"]
    )


def test_scrap(test_session, otodom_settings):
    otodom_settings.BASE_SEARCH_URL = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"

    otodom = Otodom(otodom_settings, test_session)

    scrapped_data, statistics = otodom.scrap()

    assert isinstance(scrapped_data, pd.DataFrame)
    assert len(scrapped_data.index) == 75
