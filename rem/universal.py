from typing import TextIO

import requests
from bs4 import BeautifulSoup
from requests import Response


def get_website(url: str) -> Response:
    page = requests.get(url)
    return page


def get_html_doc(response):
    page = response.text
    return page


def get_soup(html_doc: TextIO):
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def get_soup_from_url(url):
    page = get_website(url)
    html = get_html_doc(page)
    soup = get_soup(html)
    return soup
