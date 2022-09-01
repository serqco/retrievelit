import logging

import bibtexparser

import utils

logger = logging.getLogger(__name__)

def build_bibtex(data):
    logger.info('Building bibtex entries.')
    bibtex = []
    for publication in data:
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
        bibtex.append(entry)
    bibtex_db = bibtexparser.bibdatabase.BibDatabase()
    bibtex_db.entries = bibtex
    return bibtex_db

def save_to_file(data, file):
    logger.info('Creating bibtex file.')
    with open(file, 'w', encoding='utf-8') as f:
        bibtexparser.dump(data, f)
    logger.info(f'Wrote data to bibtex file {file}')

def generate_bibtex(metadata_file, bibtex_file):
    metadata = utils.load_metadata(metadata_file)
    bibtex_data = build_bibtex(metadata)
    save_to_file(bibtex_data, bibtex_file)
    
if __name__ == '__main__':
    # generate_bibtex()
    logger.error('Not a standalone file. Please run the main script instead.')