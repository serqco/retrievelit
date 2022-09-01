import json
import logging
import argparse
import os
import sys

import log_config
import setup
import downloader_pipeline
import mapper_factory
import dblp
import venues
import names
import bibtex
import pdf
import doi

# disable logging from urllib3 library (used by requests)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# TODO logger doesn't use utf-8 right now
logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(description="Downloads metadata and publication PDFs of a specified venue-volume combination. See README.md for more information.")

    parser.add_argument('target', help="the venue-volume combination to be downloaded e. g. 'ESE-2021'")
    parser.add_argument('existing_folders', nargs='*', help="existing folders in the current directory containing previous downloads, creating the namespace for the target's data")

    grouping_options = ['year', 'volume']
    parser.add_argument('--grouping', choices=grouping_options, default='year', help="wether the number after the target determines the year or volume of the choosen corpus. (default: %(default)s)")
    parser.add_argument('--mapper', default='HtmlParserMapper', help="the class in the 'doi_pdf_mappers' folder to use for retrieving the PDF URL from the DOI of a publication. (default: %(default)s). Check the 'doi_pdf_mappers' folder to see all possible mappers and the README.md on how to implement your own.")
    metadata_options = ['dblp', 'crossref']
    parser.add_argument('--metadata', choices=metadata_options, default='dblp', help="the source for metadata and DOIs of the venue. (default: %(default)s)")
    parser.add_argument('--ieeecs', action='store_true', help="rewrite DOIs pointing to ieeexplore to computer.org instead. (default: %(default)s)")
    return parser

def get_venue(target):
    venue_string = target.split('-')[0]
    logger.debug(f'Target venue-string {venue_string} read from input.')
    try:
        venue = venues.VENUES[venue_string]
    except KeyError:
        logger.error(f"No venue found matching {venue_string}. Please check your spelling or edit 'venues.py' if it should exist.")
        sys.exit(1)
    return venue

def get_number(target):
    value = target.split('-')[1]
    logger.debug(f'Target year or volume {value} read from input.')
    return value

#TODO maybe own class
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
    do_doi_rewrite = args.ieeecs
    grouping = args.grouping
    mapper_name = args.mapper

    state_file = f'{target}_state.json'
    metadata_file = 'metadata.json'
    bibtex_file = f'{target}-{metadata_source}.bib'
    list_file = f'{target}.list'
    
    venue = get_venue(target)
    number = get_number(target)
    
    # setup folder and state file
    file_setup = setup.Setup(target, state_file)
    file_setup.run()
    
    # create pipeline with all downloader steps
    pipeline = downloader_pipeline.DownloaderPipeline(state_file)
    metadata_downloader = dblp.DblpDownloader(venue, number, grouping)
    pipeline.add_step(metadata_downloader)
    name_generator = names.NameGenerator(existing_folders)
    pipeline.add_step(name_generator)
    bibtex_builder = bibtex.BibtexBuilder(bibtex_file)
    pipeline.add_step(bibtex_builder)
    doi_resolver = doi.DoiResolver(do_doi_rewrite)
    pipeline.add_step(doi_resolver)
    mapper = mapper_factory.get_mapper(mapper_name)
    pdf_downloader = pdf.PdfDownloader(mapper, target, list_file)
    pipeline.add_step(pdf_downloader)
    
    pipeline.run()
    
    delete_files([metadata_file, state_file])
    logger.info('Exiting.')


if __name__ == '__main__':
    # get cli arguments
    parser = create_parser()
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        logger.error('Manual interruption - cancelling.')
        sys.exit(1)
    