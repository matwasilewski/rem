from rem import main


def test_parse_url() -> None:
    arguments = ["--url", "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"]
    parsed = main.parse_args(arguments)

    assert parsed.url == "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa?page=1&limit=72"
