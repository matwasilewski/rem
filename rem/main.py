import argparse
import logging
import sys

import validators

logging.basicConfig(filename='otodom.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %('
                           'levelname)s - %(message)s')


# setup argparser with: propertytype, rentaltype, city, savephotos
def parse_args(args):
    # @TODO: Add parser.add_argument('-sp', '--savephotos', dest='savephotos' ...)

    parser = argparse.ArgumentParser(description='Provide input scrapper args')

    # @TODO: Add url validator
    parser.add_argument('--url', nargs="?", required=True,
                        help='Enter otodom search url')

    parser.add_argument('--page_limit', nargs="?", required=False,
                        type=int, default=1,
                        help='Enter otodom search url')


    return parser.parse_args(args)


# create all necessary urls and dirs based on categories
# return dictionary {page_url : path_to_saving_data}
def get_urls_dirs(args):
    urls_data = {}

    for propertytype in args.propertytype:
        for rentaltype in args.rentaltype:
            for city in args.city:
                pass
                # @FIXME
                # if rentaltype == 'selling' and propertytype == 'room':
                #     continue
                # main_url = ParseResult(scheme='https', netloc=hostURL,
                #                         path=(f'{typesPL.get(rentaltype)}/'+
                #                             f'{typesPL.get(propertytype)}/'+
                #                             f'{city.lower()}/'), params='',
                #                         query=(f'nrAdsPerPage={offersPerPage}'),
                #                         fragment='').geturl()
                # json_path = f'{rentaltype}-{propertytype}-{city.lower()}'
                # urls_data[main_url] = json_path
    return urls_data


def main():
    parser = parse_args(sys.argv[1:])
    args = get_args()

    urls_dirs = get_urls_dirs(args)

    # proceed(urls_dirs, args.savephotos)


if __name__ == "__main__":
    main()
