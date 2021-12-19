import argparse
import sys
from rem.logger import log

from rem.config import settings
from rem.otodom import Otodom


# setup argparser with: propertytype, rentaltype, city, savephotos
def parse_args(args):
    # @TODO: Add parser.add_argument('-sp', '--savephotos', dest='savephotos' ...)

    parser = argparse.ArgumentParser(description='Provide input scrapper args')

    # @TODO: Add url validator
    parser.add_argument(
        '--url', nargs="?", required=True, help='Enter otodom search url'
    )
    parser.add_argument(
        '--page_limit',
        nargs="?",
        required=False,
        type=int,
        default=0,
        help='Enter otodom search url',
    )
    parser.add_argument(
        '--data_file_name',
        nargs="?",
        required=False,
        type=str,
        help='Enter data file name',
    )
    parser.add_argument(
        '--data_directory',
        nargs="?",
        required=False,
        type=str,
        default="data",
        help='Enter data directory',
    )
    parser.add_argument(
        '--use_gcp',
        nargs="?",
        required=False,
        type=bool,
        default=False,
        help='Use GCP API',
    )
    parser.add_argument(
        '--save_to_file',
        nargs="?",
        required=False,
        default=True,
        type=bool,
        help='Should the result be saved in a file',
    )
    parser.add_argument(
        '--offset',
        nargs="?",
        required=False,
        default=0.0,
        type=float,
        help='Offset between queries',
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    log.info(f"Starting scrapping of {args.url}...")

    settings.BASE_SEARCH_URL = args.url

    if args.page_limit:
        settings.PAGE_LIMIT = args.page_limit
    if args.offset:
        settings.OFFSET = args.offset

    log.info(f"Config set to: {settings}")

    scraper = Otodom()
    data, statistics = scraper.scrap()


if __name__ == "__main__":
    main()
