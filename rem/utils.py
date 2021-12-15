import logging


def _extract_divs(soup, soup_filter, what: str):
    divs = soup.find_all(attrs=soup_filter)

    if len(divs) > 1:
        _log_wrong_number(len(divs), 1, what)
        return None
    elif len(divs) == 0:
        _log_wrong_number(0, 1, what)
        return None
    nested_div = list(divs[0].children)

    return nested_div


def _log_wrong_number(actual: int, expected: int, what: str) -> None:
    logging.error(
        f"{actual} {what} found for the listing, "
        f"instead of expected {expected}. Skipping the record."
    )


def _log_unexpected(unexpected: str, where: str) -> None:
    logging.error(
        f"Unexpected {unexpected} encountered in {where} in the listing"
    )
