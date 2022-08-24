import json
import logging
import argparse
import os

import log_config
import setup
import dblp
import venues
import names
import bibtex
import pdf

# disable logging from urllib3 library (used by requests)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# TODO logger doesn't use utf-8 right now
logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(description="Downloads metadata and publication PDFs of a specified venue-volume combination. See README.md for more information.")

    parser.add_argument('target', help="the venue-volume combination to be downloaded e. g. 'ESE-2021'")
    parser.add_argument('existing_folders', nargs='*', help="existing folders in the current directory containing previous downloads, creating the namespace for the target's data")

    metadata_options = ['dblp', 'crossref']
    parser.add_argument('--metadata', choices=metadata_options, default='dblp', help="the source for metadata and DOIs of the venue (default: %(default)s)")
    parser.add_argument('--ieeecs', action='store_true', help="rewrite DOIs pointing to ieeexplore to computer.org instead")
    return parser

def load_state(state_file):
    logger.info('Loading state.')
    with open(state_file, 'r') as f:
        state = json.load(f)
    return state

def update_state(state, state_file):
    # no need to update current state object, since we will only
    # read the previous steps' state if we rerun the whole program
    logger.debug('Updating state file.')
    with open(state_file, 'w') as f:
        f.write(json.dumps(state))
    logger.debug('Finished saving state.')

def download_metadata(state, target, metadata_file, state_file):
    def get_venue():
        venue = target.split('-')[0]
        logger.debug(f'Target venue {venue} read from input.')
        return venues.VENUES[venue]
    def get_year():
        year = target.split('-')[1]
        logger.debug(f'Target year {year} read from input.')
        return year

    if not state.get('metadata_download'):
        venue = get_venue()
        year = get_year()
        dblp.download_metadata(venue, year, metadata_file)
        logger.info('Done downloading metadata.')
        state['metadata_download'] = True
        update_state(state, state_file)
    else:
        logger.info('Metadata already downloaded. Skipping.')

def add_identifiers(state, metadata_file, state_file, existing_folders):
    if not state.get('identifier'):
        names.add_identifiers(metadata_file, existing_folders)
        logger.info('Done adding identifiers.')
        state['identifier'] = True
        update_state(state, state_file)
    else:
        logger.info('Identifiers already added. Skipping.')

def generate_bibtex(state, metadata_file, bibtex_file, state_file):
    if not state.get('bibtex'):
        bibtex.generate_bibtex(metadata_file, bibtex_file)
        logger.info('Done creating bibtex file.')
        state['bibtex'] = True
        update_state(state, state_file)
    else:
        logger.info('Bibtex file already built. Skipping.')

def download_pdfs(state, metadata_file, do_doi_rewrite, folder_name, state_file, list_file):
    if not state.get('pdf'):
        pdf.download_pdfs(metadata_file, do_doi_rewrite, folder_name, list_file)
        logger.info('Done downloading PDFs.')
        state['pdf'] = True
        update_state(state, state_file)
    else:
        logger.info('PDFs already downloaded. Skipping.')

def delete_files(files):
    logger.info('Deleting intermediate files.')
    for f in files:
        try:
            os.remove(f)
            logger.debug(f'Deleted file {f}.')
        except FileNotFoundError:
            logger.warn(f'Could not find file {f} for deletion.')
    logger.info('Finished deleting files.')
    




def main(args):
    logger.debug(f'Configuration: {vars(args)}')
    target = args.target
    metadata_source = args.metadata
    existing_folders = args.existing_folders

    state_file = f'{target}_state.json'
    metadata_file = f'{target}_metadata.json'
    bibtex_file = f'{target}-{metadata_source}.bib'
    list_file = f'{target}.list'

     # setup folder and state file
     # TODO folder name should contain metadata source if not dblp
     # -> only search for the combinaiton to resume state as well
    setup.main(target, state_file)
    # load state file
    state = load_state(state_file)
    # TODO refactor as not to pass so many arguments everywhere
    download_metadata(state, target, metadata_file, state_file)
    add_identifiers(state, metadata_file, state_file, existing_folders)
    generate_bibtex(state, metadata_file, bibtex_file, state_file)
    download_pdfs(state, metadata_file, args.ieeecs, target, state_file, list_file)
    delete_files([metadata_file, state_file])
    logger.info('Exiting.')


if __name__ == '__main__':
    # get cli arguments
    parser = create_parser()
    args = parser.parse_args()
    main(args)
    