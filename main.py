import argparse
import logging
import os
import sys
import typing as tg

import log_config
import setup
import downloader_pipeline
import mapper_factory
import bibtex
import dblp
import names
import pdf
import doi
import venues

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper
from doi_pdf_mappers.abstract_resolved_doi_mapper import ResolvedDoiMapper
from doi_pdf_mappers.elsevier import ElsevierMapper

# disable logging from urllib3 library (used by requests)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# TODO logger doesn't use utf-8 right now
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Set up and return the parser for passed arguments."""
    parser = argparse.ArgumentParser(description="Downloads metadata and publication PDFs of a specified venue-volume combination. See README.md for more information.")

    parser.add_argument('target', help="the venue-volume combination to be downloaded e. g. 'ESE-2021'")
    parser.add_argument('existing_folders', nargs='*', 
                        help=("existing folders in the current directory containing previous downloads, "
                              "constraining the namespace for the target's data"))
    grouping_options = ['year', 'volume']
    parser.add_argument('--grouping', choices=grouping_options, default='year', 
                        help="whether the number after the target determines the year or volume of the choosen corpus. (default: %(default)s)")
    parser.add_argument('--mapper', default='HtmlParserMapper', choices=mapper_factory.mapper_names(),
                        help=("the doi_pdf_mappers class to use for retrieving the PDF URL from the DOI of a publication. "
                              "See README.md on how to implement your own.")),
    metadata_options = ['dblp', 'crossref']
    parser.add_argument('--metadata', choices=metadata_options, default='dblp', help="the source for metadata and DOIs of the venue. (default: %(default)s)")
    parser.add_argument('--ieeecs', action='store_true', help="rewrite DOIs pointing to ieeexplore to computer.org instead. (default: %(default)s)")
    return parser

def get_venue(target: str) -> tg.Dict:
    """Return the specified venue data, if it exists."""
    venue_string = target.split('-')[0]
    logger.debug(f'Target venue-string {venue_string} read from input.')
    try:
        venue = venues.VENUES[venue_string]
    except KeyError:
        logger.error(f"No venue found matching {venue_string}. Please check your spelling or edit 'venues.py' if it should exist.")
        raise SystemExit()
    return venue

def get_number(target: str) -> str:
    """Return the number part of the target string."""
    value = target.split('-')[1]
    logger.debug(f'Target year or volume {value} read from input.')
    return value

def is_doi_resolving_needed(mapper: tg.Union[DoiMapper, ResolvedDoiMapper]) -> bool:
    """Check if the chosen mapper requires its DOIs to be resolved."""
    if type(mapper).__base__ == DoiMapper:
        logger.debug(f"Mapper {mapper} uses pure DOIs. DOI resolving will not be run.")
        return False
    elif type(mapper).__base__ == ResolvedDoiMapper:
        logger.debug(f"Mapper {mapper} uses resolved DOIs. Resolving will be run.")
        return True
    else:
        logger.error(f"Class {type(mapper)} doesn't inherit from DoiMapper, nor ResolvedDoiMapper.")
        raise SystemExit()

def is_selenium_needed(mapper: tg.Union[DoiMapper, ResolvedDoiMapper]) -> bool:
    """Check if the chosen mapper requires Selenium to download."""
    if isinstance(mapper, ElsevierMapper):
        logger.debug(f"Mapper {mapper} is of type `ElsevierMapper`. The downloader will use Selenium to get the PDF files.")
        return True
    else:
        logger.debug(f"Mapper {mapper} does not require Selenium to download the PDF files. The downloader will use requests to get the PDF files.")
        return False


#TODO maybe own class
def delete_files(files: tg.Sequence[str]) -> None:
    """Delete the specified files."""
    logger.info('Deleting intermediate files.')
    for f in files:
        try:
            os.remove(f)
            logger.debug(f'Deleted file {f}.')
        except FileNotFoundError:
            logger.warning(f'Could not find file {f} for deletion.')
    logger.info('Finished deleting files.')
    

def main(args: argparse.Namespace) -> None:
    """Run the downloader pipeline using the settings in args."""
    logger.debug(f'Configuration: {vars(args)}')
    target = args.target
    metadata_source = args.metadata
    existing_folders = args.existing_folders
    do_doi_rewrite = args.ieeecs
    grouping = args.grouping
    mapper_name = args.mapper

    state_file = f'{target}_state.json'
    metadata_file = f'{target}-metadata.json'
    bibtex_file = f'{target}-{metadata_source}.bib'
    list_file = f'{target}.list'
    
    venue = get_venue(target)
    number = get_number(target)
    
    mapper = mapper_factory.get_mapper(mapper_name)
    resolve_dois = is_doi_resolving_needed(mapper)
    use_selenium = is_selenium_needed(mapper)
    
    file_setup = setup.Setup(target, state_file, use_selenium)
    file_setup.run()
    
    # create pipeline with all downloader steps
    pipeline = downloader_pipeline.DownloaderPipeline(state_file)
    metadata_downloader = dblp.DblpDownloader(metadata_file, venue, number, grouping)
    pipeline.add_step(metadata_downloader)
    name_generator = names.NameGenerator(metadata_file, existing_folders, append_keyword=False)
    pipeline.add_step(name_generator)
    bibtex_builder = bibtex.BibtexBuilder(metadata_file, bibtex_file)
    pipeline.add_step(bibtex_builder)
    if resolve_dois:
        doi_resolver = doi.DoiResolver(metadata_file, do_doi_rewrite)
        pipeline.add_step(doi_resolver)
    pdf_downloader = pdf.PdfDownloader(metadata_file, mapper, target, list_file, resolve_dois, use_selenium)
    pipeline.add_step(pdf_downloader)
    
    pipeline.run()
    
    delete_files([state_file])

    logger.info('Exiting.')


if __name__ == '__main__':
    # get cli arguments
    parser = create_parser()
    args = parser.parse_args()
    try:
        main(args)
    except SystemExit:
        logger.info('Exiting.')
        sys.exit(1)
    except KeyboardInterrupt:
        logger.error('Manual interruption - cancelling.')
        sys.exit(1)
    