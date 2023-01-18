import logging
import time
import typing as tg
from pathlib import Path

import requests

from retrievelit import utils
from retrievelit.pipeline_step import PipelineStep
from retrievelit.exceptions import NoEntriesReceivedError

logger = logging.getLogger(__name__)

BASE_URL = 'https://dblp.org/db/'
API_BASE_URL = 'https://dblp.org/search/publ/api?q='

class DblpDownloader(PipelineStep):
    """Download metadata for a target from dblp.org and store it in a uniform format."""
    def __init__(self, metadata_file: Path, venue: tg.Mapping, number: str, grouping: str) -> None:
        self._metadata_file = metadata_file
        self._venue = venue
        self._number = number
        self._grouping = grouping
        # mds = metadata-source
        self._mds_config: tg.Dict = {}

    def _verify_mds_config(self) -> None:
        """Verify that the venue dict contains all fields needed by the downloader."""
        try:
            mds_config = self._venue['metadata_sources']['dblp']
            venue_type = mds_config['type']
            acronym = mds_config['acronym']
            if not venue_type: raise ValueError('\'type\'')
            if not acronym: raise ValueError('\'acronym\'')
        except (KeyError, ValueError) as e:
            logger.error(f"Value missing from venues.py: {str(e)}. Please make sure the configuration"
                          "adheres to the expected format, or try another metadata-source.")
            raise SystemExit()
        allowed_venue_types = ['journals', 'conf']
        if venue_type not in allowed_venue_types:
            logger.error("Incorrect value for 'type' in 'venues.py' configuration."
                         f"Value must be one of {allowed_venue_types}. Value is '{venue_type}'.")
            raise SystemExit()

    def _load_mds_config(self) -> None:
        """Load the fields of the venue dict containing required information to download the metadata from dblp."""
        self._mds_config = self._venue['metadata_sources']['dblp']

    def _get_data_for_year(self) -> tg.List:
        """Download the metadata of the venue for the specified year."""
        venue_type = self._mds_config['type']
        acronym = self._mds_config['acronym']
        offset = 0
        received = 0
        entries = []
        while True:
            url = f"{API_BASE_URL}stream:streams/{venue_type}/{acronym}:&h=1000&f={offset}&format=json"
            data = self._get_data(url)
            hits = data['result']['hits']
            received += int(hits['@sent'])
            total = int(hits['@total'])
            logger.debug(f"Received {received} entries. Amount in collection: {total}.")
            if hits['@sent'] == '0':
                logger.warning('No entries received. This might be due to the hard cap of 10000 computed entries.'
                               'If you are downloading entries older than ~15 years, please download a specific volume instead.')
                break
            entries.extend(hits['hit'])
            older_year_reached = entries[-1]['info']['year'] < self._number  # entries arrive youngest first
            if received >= total or older_year_reached:
                logger.debug(f"Received all entries.")
                break
            logger.debug(f"{total - received} entries left. Getting next batch.")
            offset += 1000
            time.sleep(1)
            
        if not entries:
            raise NoEntriesReceivedError()
        logger.debug(f"{len(entries)} entries received from publ API.")
        logger.debug("Filtering out entries from other years.")
        year_entries = [e for e in entries if e['info']['year'] == self._number]
        logger.debug(f"{len(year_entries)} entries found for year {self._number}.")
        return year_entries
        
    def _build_volume_url(self) -> str:
        """Generate the dbl URL to download the specified volume of the venue."""
        venue_type = self._mds_config['type']
        acronym = self._mds_config['acronym']
        url = f"{API_BASE_URL}toc:db/{venue_type}/{acronym}/{acronym}{self._number}.bht:&h=1000&format=json"
        logger.debug(f'Built volume url: {url}')
        return url

    def _get_data(self, url: str) -> tg.Dict:
        """Send a get request to the URL and return the json data, if successful."""
        logger.debug(f'GET request to {url}')
        r = requests.get(url)
        logger.debug(f'Reponse code: {r.status_code}')
        r.raise_for_status()
        return r.json()

    def _get_data_for_volume(self) -> tg.List:
        """Download the metadata of the venue for the specified volume."""
        volume_url = self._build_volume_url()
        data = self._get_data(volume_url)
        if data['result']['hits']['@total'] == "0":
            raise NoEntriesReceivedError()
        entries = data['result']['hits']['hit']
        logger.debug(f"Received {len(entries)} entries for volume {self._number}.")
        return entries

    def _unify_data_format(self, hits: tg.List) -> tg.List:
        """Rewrite the dblp metadata into a uniform format."""
        result = []
        for publication in hits:
            publication = publication['info']

            keys = ['title', 'volume', 'number', 'pages', 'year', 'type', 'doi']
            # only journals have volume and number fields
            entry = {key: publication.get(key) for key in keys}
            if not entry.get('doi'):
                logger.warning(f"Dropped entry without DOI: {publication}")
                continue
            # dblp returns DOIs in uppercase, which e. g. SciHub can't handle.
            entry['doi'] = entry['doi'].lower()
            entry['venue'] = self._venue['name']
            entry['venue_type'] = self._venue['type']
            
            # create list of author names
            authors = publication.get('authors')
            if not authors:
                logger.warning(f"Dropped entry without author: {publication}")
                continue

            author = authors['author']
            # dblp author value sometimes contains numbers at the end (e. g. "Max Mueller 001")
            # so strip numbers and whitespace
            strip_values = "0123456789" + " "
            # field 'author' can be a single value or a list in the json returned from dblp
            if isinstance(author, list):
                entry['authors'] = [e['text'].strip(strip_values) for e in author]
            elif isinstance(author, dict):
                # create list with 1 element here to get rid of this check in the next steps
                entry['authors'] = [author['text'].strip(strip_values)]
            entry['pdf'] = False

            logger.debug(f'created entry: {entry}')
            result.append(entry)
        return result

    def run(self) -> None:
        """Download the dblp metadata for the specified target and save it to a file."""
        self._verify_mds_config()
        # mds = metadata-source
        self._load_mds_config()
        
        # Treat year as volume number for ICSE Technical Track, since it's hard to distinguish
        # between Tracks when using the dblp publication API because of result cap
        if self._mds_config['acronym'] == 'icse' and self._grouping == 'year':
            logger.warn(f"Using --grouping=volume instead to download Technical Track of ICSE. See README.md for more information.")
            self._grouping = 'volume'

        logger.debug(f'Downloading metadata for:')
        logger.debug(f'venue: {self._venue}')
        logger.debug(f'year or volume: {self._number}')
        logger.debug(f'grouping: {self._grouping}')
        
        try:
            if self._grouping == 'year':
                raw_data = self._get_data_for_year()
            if self._grouping == 'volume':
                raw_data = self._get_data_for_volume()
        except NoEntriesReceivedError:
            logger.error("No entries received from publ API. This could be due to:\n"
                         f"- an incorrect volume/year value (current value is '{self._number}' for grouping '{self._grouping}')\n"
                         "- an incorrect value in the 'acronym' field in 'venues.py'"
                         " or a combination of 'type' and 'acronym' that doesn't exist.\n"
                         f"Current values: {self._mds_config}.\n"
                         "Please check your configuration and make sure the values match the data on dblp.org.\n"
                         "See 'https://github.com/serqco/retrievelit#adding-a-venue' for more information.")
            raise SystemExit()

        logger.debug('Metadata received.')
        logger.debug('Rewriting data in uniform format.')
        unified_data = self._unify_data_format(raw_data)
        utils.save_metadata(self._metadata_file, unified_data)

if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')
