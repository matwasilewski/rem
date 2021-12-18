# real-estate-monitoring

This is a personal package for data scrapping and dataset generation for polish real estate market.

## Set-up

To download and install depenencies of the project:

1. `poetry install && poetry update`

If you want to use the GCP-based functionalities:
2. Copy your GCP API key to `secrets/GCP_API_KEY`


3. Copy contents of `.env_example` to a new file in the same directory called `.env`.


## Configuration

`.env_example` contains what we consider sensible testing settings, but to change query URL, destination for GCP queries, page limit or offsets change the appropriate settings in the new .env file. 
Environment variables always take precedence over variables set in `.env`
Some settings can also be passed via the command line - to see the available options, run

`poetry run python main.py --help`

## Usage

`poetry run python main.py`

