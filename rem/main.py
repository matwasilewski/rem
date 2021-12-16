import argparse
import logging
import sys

from rem.otodom import Otodom

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
        default="gcp_api.key",
        type=str,
        help='GCP key path',
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
        default=0,
        type=int,
        help='Offset between queries',
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    logging.info(f"Starting scrapping of {args.url}...")

    scrapper = Otodom(base_search_url=args.url,
                      data_file_name=args.data_file_name,
                      data_directory=args.data_directory,
                      page_limit=args.page_limit,
                      use_google_maps_api=args.use_gcp,
                      gcp_api_key_path=args,
                      save_to_file=args.save_to_file,
                      offset=args.offset,
                      )

    data = scrapper.scrap()


if __name__ == "__main__":
    main()
