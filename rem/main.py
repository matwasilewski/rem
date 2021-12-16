import argparse
import logging
import sys

import validators

from rem import otodom

logging.basicConfig(
    filename='otodom.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(threadName)s -  %('
    'levelname)s - %(message)s',
)


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
        default=1,
        help='Enter otodom search url',
    )
    parser.add_argument(
        '--data_file_name',
        nargs="?",
        required=True,
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
        '--gcp_key_path',
        nargs="?",
        required=False,
        type=str,
        help='GCP key path',
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    logging.info(f"Starting scrapping of {args.url}...")
    scrapped_data = otodom.otodom_scrap(args.url, args.page_limit)


if __name__ == "__main__":
    main()
