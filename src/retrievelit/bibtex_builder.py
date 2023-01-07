import logging
import typing as tg

import bibtexparser

from retrievelit import utils
from retrievelit.pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

class BibtexBuilder(PipelineStep):
    """Populate the bibtex file based on the data in metadata_file."""
    def __init__(self, metadata_file: str, bibtex_file: str):
        self._metadata_file = metadata_file
        self._bibtex_file = bibtex_file
        self._metadata: tg.List = []
        self._bibtex_db: bibtexparser.bibdatabase.BibDatabase = bibtexparser.bibdatabase.BibDatabase()
    
    def _build_entry(self, publication: tg.Dict) -> tg.Dict:
        """Create the article entry for the bibtex file in the format bibtexparser expects."""
        entry = {
            'ENTRYTYPE': 'article',
            'ID': publication['identifier'],
            #TODO build names with bibtex standard (last, first??)
            'author': ' and '.join(publication['authors']),
        }
        fields = ['title', 'venue', 'volume', 'number', 'pages', 'year', 'type', 'doi']
        for field in fields:
            # volume and number are None for conferences, so exclude these from .bib file
            if publication.get(field):
                entry[field] = publication[field]
        logger.debug(f'Built bibtex entry: {entry}')
        return entry
    
    def _build_bibtex(self) -> None:
        """Create the bibtex entries and write them to the bibtex database object."""
        logger.debug('Building bibtex entries.')
        bibtex = [self._build_entry(e) for e in self._metadata]
        self._bibtex_db.entries = bibtex

    def _save_to_file(self) -> None:
        """Write the bibtex database to the bibtex file."""
        logger.debug('Creating bibtex file.')
        with open(self._bibtex_file, 'w', encoding='utf-8') as f:
            bibtexparser.dump(self._bibtex_db, f)
        logger.debug(f'Wrote data to bibtex file {self._bibtex_file}')

    def run(self) -> None:
        """Run the full bibtex process."""
        self._metadata = utils.load_metadata(self._metadata_file)
        self._build_bibtex()
        self._save_to_file()
        
if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.') # pragma: no cover