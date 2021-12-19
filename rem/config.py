import datetime
import os
from functools import lru_cache
from typing import Dict, Optional, Union

import pkg_resources
import tomlkit
from pydantic import BaseSettings


def _get_project_meta(name: str = 'unknown') -> Dict:
    """
    Get name and version from pyproject metadata.
    """
    version = "unknown"
    description = ""
    try:
        with open('./pyproject.toml') as pyproject:
            file_contents = pyproject.read()
        parsed = dict(tomlkit.parse(file_contents))['tool']['poetry']
        name = parsed['name']
        version = parsed.get('version', 'unknown')
        description = parsed.get('description', '')
    except FileNotFoundError:
        # If cannot read the contents of pyproject directly (i.e. in Docker),
        # check installed package (there is a risk that this could be stale
        # though):
        try:
            distribution = pkg_resources.get_distribution(name)
            name = distribution.project_name
            version = distribution.version
        except pkg_resources.DistributionNotFound:
            pass
    return {"name": name, "version": version, "description": description}


PKG_META = _get_project_meta()


class Settings(BaseSettings):
    """
    Settings. Environment variables always take priority over values loaded
    from the dotenv file.
    """

    # Meta
    APP_NAME: str = str(PKG_META['name'])
    APP_VERSION: str = str(PKG_META['version'])
    PUBLIC_NAME: str = APP_NAME
    DESCRIPTION: str = str(PKG_META['description'])

    # Logger
    LOGGER_NAME: str = "rem"
    LOG_LEVEL: str = "info"
    VERBOSE_LOGS: Union[bool, int, str] = True
    JSON_LOGS: Union[bool, int, str] = False
    LOG_DIR: str = os.sep.join(["logs", "rem.log"])
    SYSLOG_ADDR: Optional[str] = None

    # Scraping settings
    BASE_SEARCH_URL: str
    DATA_FILE_NAME: str = "otodom"
    DATA_DIRECTORY: str = "data"
    PAGE_LIMIT: int = 1
    USE_GOOGLE_MAPS_API: bool = False
    GCP_API_KEY: str
    SAVE_TO_FILE: bool = True
    OFFSET: float = 0.0
    DOWNLOAD_LISTINGS_ALREADY_IN_FILE: bool = False
    TIME_OF_DEPARTURE: datetime.datetime = datetime.datetime(
        2021, 12, 13, 8, 00
    )
    DESTINATION: str
    TIMEOUT: int = 0
    LOAD_FROM_DATA: bool = True

    class Config:
        env_file_encoding = 'utf-8'
        case_sensitive = True
        secrets_dir = "secrets"


@lru_cache()
def get_settings() -> Settings:
    env_file = os.sep.join([os.getcwd(), ".env"])
    return Settings(_env_file=env_file)


settings = get_settings()
