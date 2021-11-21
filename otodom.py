from typing import Union, TextIO, Optional
import logging
from bs4 import BeautifulSoup
import re


def get_listing(path: Union[str, TextIO]):
    soup = BeautifulSoup(path, "html.parser")
    return soup


def get_price(soup: BeautifulSoup) -> Optional[int]:
    soup_filter = {"aria-label": "Cena"}
    price_divs = soup.find_all(attrs=soup_filter)

    if len(price_divs) > 1:
        logging.error(f"{len(price_divs)} prices found for the listing, "
                      f"instead of expected one. Skipping the record.")
        return None
    elif len(price_divs) == 0:
        logging.error(f"0 prices found for the listing, instead of expected "
                      f"one. Skipping the record.")
        return None

    price = [price for price in price_divs[0].children]
    if len(price) != 1:
        logging.error(f"{len(price)} prices found for the listing, "
                      f"instead of expected one. Skipping the record.")

    if "." or "," in price[0]:
        logging.error(f". or , encountered in price - investigate. "
                      f"Skipping the record.")

    price = int("".join(re.findall('[0-9]+', price[0])))
    return price
