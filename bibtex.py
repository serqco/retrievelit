import logging

import bibtexparser

import utils
from pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

class BibtexBuilder(PipelineStep):
    
    def __init__(self, metadata_file, bibtex_file):
        self._metadata_file = metadata_file
        self._bibtex_file = bibtex_file
        self._metadata = {}
        self._bibtex_db = bibtexparser.bibdatabase.BibDatabase()
    
    def _build_entry(self, publication):
        entry = {
            'ENTRYTYPE': 'article',
            'ID': publication['identifier'],
            #TODO build names with bibtex standard (last, first??)
            'author': ' and '.join(publication['authors']),
        }
        fields = ['title', 'venue', 'volume', 'number']
        for field in fields:
            # volume and number are None for conferences
            if publication.get(field):
                entry[field] = publication[field]
        logger.debug(f'Built bibtex entry: {entry}')
        return entry
    
    def _build_bibtex(self):
        logger.debug('Building bibtex entries.')
        bibtex = [self._build_entry(e) for e in self._metadata]
        self._bibtex_db.entries = bibtex

    def _save_to_file(self):
        logger.debug('Creating bibtex file.')
        with open(self._bibtex_file, 'w', encoding='utf-8') as f:
            bibtexparser.dump(self._bibtex_db, f)
        logger.debug(f'Wrote data to bibtex file {self._bibtex_file}')

    def run(self):
        self._metadata = utils.load_metadata(self._metadata_file)
        self._build_bibtex()
        self._save_to_file()
        
if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.') # pragma: no cover