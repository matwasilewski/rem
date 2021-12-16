import logging
import os.path
from typing import Optional, Tuple, Dict, List

import pandas as pd
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs

from rem import utils
from rem.universal import get_soup_from_url
from rem.utils import (
    _extract_divs,
    _log_wrong_number,
    _log_unexpected,
    load_data,
)
import googlemaps

OTODOM_LINK = "https://www.otodom.pl/"


class Otodom:
    def __init__(
        self,
        base_search_url,
        data_file_name,
        data_directory="data",
        page_limit=1,
        use_google_maps_api=False,
        gcp_api_key_path="gcp_api.key",
        save_to_file=True,
        offset=0,
    ):
        self.data_directory = data_directory
        self.base_search_url = base_search_url
        self.page_limit = page_limit
        self.gmaps = None
        self.data_file_name = data_file_name
        self.data = load_data(data_file_name)
        self.save_to_file = save_to_file
        self.offset = offset

        if use_google_maps_api:
            try:
                with open(gcp_api_key_path) as f:
                    gcp_key = f.read()
                    self.gmaps = googlemaps.Client(key=gcp_key)
            except FileNotFoundError:
                raise "no GCP API key provided!"

        self.listing_information_retrieval_methods = [
            self.get_listing_url,
            self.get_price,
            self.get_size,
            self.get_building_type,
            self.get_window_type,
            self.get_year_of_construction,
            self.get_number_of_rooms,
            self.get_condition,
            self.get_floor,
            self.get_monthly_fee,
            self.get_unique_id,
            self.get_ownership_form,
            self.get_construction_material,
            self.get_market_type,
            self.get_heating,
        ]

    def scrap(self):
        dataframe = pd.DataFrame()
        generator = self.url_generator()

        # @TODO: Add update option
        for url_count, url in enumerate(generator):
            if url_count == self.page_limit:
                break

            search_soup = get_soup_from_url(url, offset=self.offset)

            listings_urls = self.get_all_listing_urls_for_page(search_soup)
            if len(listings_urls) == 0:
                break
            listing_soups = [get_soup_from_url(url, self.offset) for url in listings_urls]

            self.process_listing_soups(listing_soups)

        if self.save_to_file:
            utils.save_data(
                self.data, self.data_file_name, self.data_directory
            )

        return dataframe

    def process_listing_soups(self, listings: List[BeautifulSoup]):
        for listing in listings:
            listing_data = self.get_data_from_listing(listing)
            self.add_new_listing_data(listing_data)

    def url_generator(self):
        parsed_url = urlparse(self.base_search_url)
        page_value = int(parse_qs(parsed_url.query).get("page", [1])[0])
        limit_value = int(parse_qs(parsed_url.query).get("limit", [36])[0])
        base_url = (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        )
        while True:
            yield f"{base_url}?page={page_value}&limit={limit_value}"
            page_value += 1

    def get_data_from_listing(self, listing):
        listing_data: pd.Series = pd.Series()

        for listing_extractor in self.listing_information_retrieval_methods:
            try:
                outcome = listing_extractor(listing)
            except Exception as e:
                logging.error(f"Exception in extractor {listing_extractor}: {e}")ž
            data = pd.Series()
            listing_data = listing_data.append(data)

        return listing_data

    def add_new_listing_data(self, listing_data: pd.Series):
        self.data = self.data.append(listing_data, ignore_index=True)

    def get_all_listing_urls_for_page(self, search_soup):
        lis_standard = self.get_standard_listing_urls_for_page(search_soup)
        lis_promoted = self.get_promoted_listing_urls_for_page(search_soup)
        if len(lis_standard) == 0:
            return []
        else:
            return lis_promoted + lis_standard

    def get_promoted_listing_urls_for_page(self, soup: BeautifulSoup):
        promoted_filter = {"data-cy": "search.listing.promoted"}
        promoted_div = soup.find(attrs=promoted_filter)
        lis = promoted_div.findAll("li")
        return self.get_listing_urls_from_search_page(lis)

    def get_standard_listing_urls_for_page(self, soup: BeautifulSoup):
        standard_filter = {"data-cy": "search.listing"}
        divs = soup.find_all(attrs=standard_filter)
        if len(divs) < 2:
            return []
        standard_divs = divs[1]
        lis = standard_divs.findAll("li")
        return self.get_listing_urls_from_search_page(lis)

    @staticmethod
    def get_listing_urls_from_search_page(lis):
        links = []
        for li in lis:
            local_links = []
            for element in li:
                if element.has_attr("href"):
                    local_links.append(element["href"])
            if len(local_links) == 1:
                links.append("https://www.otodom.pl" + local_links[0])
            else:
                _log_wrong_number(len(local_links), 1, "listing links")
        return links

    @staticmethod
    def get_price(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
        soup_filter = {"aria-label": "Cena"}

        price_div = _extract_divs(soup, soup_filter, "price")

        if len(price_div) != 1:
            _log_wrong_number(len(price_div), 1, "price")

        if "." in price_div[0]:
            _log_unexpected(".", "price")
        elif "," in price_div[0]:
            _log_unexpected(",", "price")

        try:
            price = int(
                re.sub(
                    pattern=r"[^0-9,.]",
                    repl="",
                    string=price_div[0],
                    flags=re.UNICODE,
                )
            )
        except ValueError as e:
            logging.error(f"Can't conver the price {e}")

        return {"price": price}

    def get_size(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
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

        floor_size_float = self._resolve_floor_size(floor_size[0])

        return {"floor_size_in_m2": floor_size_float}

    @staticmethod
    def _resolve_floor_size(floor_size: str) -> float:
        floor_size = floor_size.strip()
        floor_size = re.match("^[0-9,.]+", floor_size).group(0)
        floor_size = float(
            re.sub(pattern=",", repl=r".", string=floor_size, flags=re.UNICODE)
        )
        return floor_size

    @staticmethod
    def get_building_type(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Rodzaj zabudowy"}

        type_of_building_div = _extract_divs(
            soup, soup_filter, "type-of-building"
        )

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

    @staticmethod
    def get_window_type(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Okna"}

        type_of_window_div = _extract_divs(soup, soup_filter, "window")
        if not type_of_window_div:
            return {"windows_type": None}

        window = []

        for child in type_of_window_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Okna"
            ):
                window.append(child.contents)

        if len(window) != 1:
            _log_wrong_number(len(window), 1, "window")
            return None

        return {"windows_type": window[0][0]}

    @staticmethod
    def get_year_of_construction(
        soup: BeautifulSoup,
    ) -> Dict[str, Optional[int]]:
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

    @staticmethod
    def get_number_of_rooms(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
        soup_filter = {"aria-label": "Liczba pokoi"}

        number_of_rooms_div = _extract_divs(
            soup, soup_filter, "number_of_rooms"
        )
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

    @staticmethod
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

    @staticmethod
    def _resolve_floor(floor_string: str) -> Tuple[int, Optional[int]]:
        floor: int
        floors_in_building: Optional[int]
        floor_string = "".join(floor_string.split()).lower()

        if "\\" in floor_string or "/" in floor_string:
            temp_floor, temp_floors_in_building = floor_string.split("/")
            if temp_floor == "parter":
                floor = 0
                floors_in_building = (
                    int(temp_floors_in_building)
                    if temp_floors_in_building
                    else None
                )
            else:
                floor = int(temp_floor)
                floors_in_building = (
                    int(temp_floors_in_building)
                    if temp_floors_in_building
                    else None
                )
        elif floor_string == "parter":
            floor = 0
            floors_in_building = None
        else:
            floor = int(floor_string)
            floors_in_building = None

        return floor, floors_in_building

    @staticmethod
    def get_total_floors_in_building(soup: BeautifulSoup):
        soup_filter = {"aria-label": "Liczba pięter"}

        floors_in_building_div = _extract_divs(
            soup, soup_filter, "floors_in_building"
        )
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

    def get_floor(self, soup: BeautifulSoup):
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

        floor, floors_in_building = self._resolve_floor(floor_list[0][0])
        if floors_in_building is None:
            floors_in_building = self.get_total_floors_in_building(soup)

        return {
            "floor": floor,
            "floors_in_building": floors_in_building["floors_in_building"],
        }

    @staticmethod
    def resolve_monthly_fee(monthly_fee_string: str):
        monthly_fee: float
        monthly_fee_string = "".join(monthly_fee_string.split()).lower()

        if "zł" in monthly_fee_string:
            monthly_fee_string = monthly_fee_string.replace("zł", "")
        elif "pln" in monthly_fee_string:
            monthly_fee_string = monthly_fee_string.replace("pln", "")

        monthly_fee_string = re.sub(",", ".", monthly_fee_string)
        monthly_fee_string = monthly_fee_string.strip()
        monthly_fee = float(monthly_fee_string)
        monthly_fee = round(monthly_fee, 0)
        return monthly_fee

    def get_monthly_fee(self, soup: BeautifulSoup):
        soup_filter = {"aria-label": "Czynsz"}

        monthly_fee_div = _extract_divs(soup, soup_filter, "monthly_fee")
        if not monthly_fee_div:
            return {"monthly_fee": None}

        monthly_fee_list = []

        for child in monthly_fee_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Czynsz"
            ):
                monthly_fee_list.append(child.contents)

        if len(monthly_fee_list) != 1:
            _log_wrong_number(len(monthly_fee_list), 1, "monthly_fee")
            return None

        monthly_fee = self.resolve_monthly_fee(monthly_fee_list[0][0])

        return {"monthly_fee": monthly_fee}

    @staticmethod
    def get_unique_id(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
        tags_content = []

        for tags in soup.find_all('meta'):
            tags_content.append(tags.get('content'))

        indices = []
        for i, elem in enumerate(tags_content):
            if elem and 'www.otodom.pl' in elem:
                indices.append(i)

        contem_elements_list = []
        for i in indices:
            contem_elements_list.append(tags_content[i])

        id_candidate = []
        for element in contem_elements_list:
            id_string = re.search(r"(?<!\d)\d{8}(?!\d)", element)
            if id_string:
                id_candidate.append(id_string.group(0))

        unique_id = int(id_candidate[0])

        if not unique_id:
            return {"unique_id": None}

        return {"unique_id": unique_id}

    @staticmethod
    def get_ownership_form(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Forma własności"}

        ownership_div = _extract_divs(soup, soup_filter, "ownership_form")
        if not ownership_div:
            return {"ownership_form": None}

        ownership = []

        for child in ownership_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Forma własności"
            ):
                ownership.append(child.contents)

        if len(ownership) != 1:
            _log_wrong_number(len(ownership), 1, "ownership_form")
            return None

        return {"ownership_form": ownership[0][0]}

    @staticmethod
    def get_market_type(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Rynek"}

        market_div = _extract_divs(soup, soup_filter, "market_type")
        if not market_div:
            return {"market_type": None}

        market = []

        for child in market_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Rynek"
            ):
                market.append(child.contents)

        if len(market) != 1:
            _log_wrong_number(len(market), 1, "market_type")
            return None

        return {"market_type": market[0][0]}

    @staticmethod
    def get_construction_material(
        soup: BeautifulSoup,
    ) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Materiał budynku"}

        material_div = _extract_divs(
            soup, soup_filter, "construction_material"
        )
        if not material_div:
            return {"construction_material": None}

        material = []

        for child in material_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Materiał budynku"
            ):
                material.append(child.contents)

        if len(material) != 1:
            _log_wrong_number(len(material), 1, "construction_material")
            return None

        return {"construction_material": material[0][0]}

    # def resolve_outdoor_space(self, outdoor_space_string: str):
    #    garden: int
    #    balcony: int
    #     terrace: int
    #
    #     outdoor_space_string = "".join(outdoor_space_string.split()).lower()
    #
    #    if "\\" in outdoor_space_string:
    #        outdoor_space_string = outdoor_space_string.replace("\\", ",")
    #    elif "/" in outdoor_space_string:
    #         outdoor_space_string = outdoor_space_string.replace("/", ",")
    #
    #    outdoor_space_list = []
    #     outdoor_space_list = outdoor_space_string.split(",")
    #
    #    if "ogród" in outdoor_space_list or "ogródek" in outdoor_space_list:
    #        garden = 1
    #    else:
    #        garden = 0
    #    if "balkon" in outdoor_space_list:
    #        balcony = 1
    #    else:
    #        balcony = 0
    #    if "taras" in outdoor_space_list:
    #        terrace = 1
    #    else:
    #         terrace = 0
    #
    #    return garden, balcony, terrace#
    #
    # def get_outdoor_space(soup: BeautifulSoup):
    #     soup_filter = {"aria-label": "Balkon / ogród / taras"}
    #
    #     outdoor_space_div = _extract_divs(soup, soup_filter, "outdoor_space")
    #     if not outdoor_space_div:
    #         breakpoint()
    # return {"outdoor_space": None}
    #
    #     outdoor_space_list = []
    #
    #     for child in outdoor_space_div:
    #         if (
    #                 child.attrs.get("title") is not None
    #                 and child.attrs.get("title") != "Balkon / ogród / taras"
    #         ):
    #             outdoor_space_list.append(child.contents)
    #
    #     garden, balcony, terrace = resolve_outdoor_space(outdoor_space_list[0][0])
    #
    #      return {"garden": garden, "balcony": balcony, "terrace": terrace}

    @staticmethod
    def get_heating(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        soup_filter = {"aria-label": "Ogrzewanie"}

        heating_div = _extract_divs(soup, soup_filter, "heating")
        if not heating_div:
            return {"heating": None}

        heating = []

        for child in heating_div:
            if (
                child.attrs.get("title") is not None
                and child.attrs.get("title") != "Ogrzewanie"
            ):
                heating.append(child.contents)

        if len(heating) != 1:
            _log_wrong_number(len(heating), 1, "heating")
            return None

        return {"heating": heating[0][0]}

    @staticmethod
    def get_address(soup: BeautifulSoup) -> dict[str, Optional[str]]:
        address_list = []
        for a in soup.findAll('a'):
            address_list.append(a.text)

        indices = []
        for i, elem in enumerate(address_list):
            if 'Warszawa' in elem:
                indices.append(i)

        contem_address_list = []
        for i in indices:
            contem_address_list.append(address_list[i])

        address = max(contem_address_list, key=len)

        return {"address": address}

    @staticmethod
    def get_listing_url(soup: BeautifulSoup):
        link = soup.select('link[rel="canonical"]')[0].get("href")
        return link

    def extract_long_lat_via_address(self, address):
        geocode_result = self.gmaps.geocode(address)
        return geocode_result
