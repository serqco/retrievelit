import argparse
import logging
import re
import sys
import typing as tg
from pathlib import Path

from retrievelit import log_config
from retrievelit import setup_files
from retrievelit import downloader_pipeline
from retrievelit import mapper_factory
from retrievelit import bibtex_builder
from retrievelit import dblp_downloader
from retrievelit import name_generator
from retrievelit import pdf_downloader
from retrievelit import venues


# disable logging from urllib3 library (used by requests)
logging.getLogger('urllib3').setLevel(logging.ERROR)

log_config.setup()
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
    parser.add_argument('--metadata', choices=metadata_options, default='dblp', 
                        help="the source for metadata and DOIs of the venue. (default: %(default)s)")
    parser.add_argument('--sample', action='store', type=int, metavar='N',
                        help="number of randomly sampled articles to retrieve the PDF for. (default: all)")
    parser.add_argument('--maxwait', action='store', type=int, metavar='N', default=20,
                        help="will wait between 0.25 N and N seconds after each download. (default: %(default)s")
    parser.add_argument('--downloaddir', action='store', type=str, metavar='fullpath', 
                        default=f"{Path.home()}/Downloads",
                        help="will wait between 0.25 N and N seconds after each download. (default: %(default)s)")
    parser.add_argument('--longname', action='store_true', 
                        help="add the first non-particle word of the publication title to it's name. (default: %(default)s)")
    return parser


def parse_target(target: str) -> tg.Tuple[tg.Mapping, str]:
    target_regexp = r"(.+)-(\d+)"
    mm = re.fullmatch(target_regexp, target)
    if not mm:
        logger.error("Malformed target specification: '%s'.\nUse format %s, e.g. %s" %
                     (target, "<venuename>-<number>", "ICSE-2024"))
        raise SystemExit
    venuename, number = mm.group(1), mm.group(2)
    if not venuename in venues.VENUES:
        logger.error("Unknown venue '%s'.\nKnown venues are: %s.\nExtend %s.py to add your own." %
                     (venuename, list(venues.VENUES), venues.__name__))
        raise SystemExit()
    return venues.VENUES[venuename], number


def main() -> None:
    """Entry point: Run the entire downloader as a CLI command."""
    argv = sys.argv[1:]
    parser = create_parser()
    args = parser.parse_args(argv)
    logger.debug(f'Configuration: {vars(args)}')

    target_dir = Path(args.target)
    metadata_dir = Path(target_dir, 'metadata')
    basename = f"{args.target}-{args.metadata}"
    metadata_file = Path(metadata_dir, f'{basename}.json')
    bibtex_file = Path(metadata_dir, f'{basename}.bib')
    list_file = Path(metadata_dir, f'{args.target}.list')

    try:
        venue, number = parse_target(args.target)
        mapperclass = mapper_factory.get_mapper(args.mapper)
        setup = setup_files.Setup(metadata_dir, metadata_file, vars(args))
        setup.run()
        # --- create pipeline with all downloader steps:
        pipeline = downloader_pipeline.DownloaderPipeline(metadata_file)
        metadata_downloader = dblp_downloader.DblpDownloader(metadata_file, venue, number, 
                                                             args.grouping, mapperclass)
        pipeline.add_step(metadata_downloader)
        name_generator_ = name_generator.NameGenerator(metadata_file, args.existing_folders, args.longname)
        pipeline.add_step(name_generator_)
        bibtex_builder_ = bibtex_builder.BibtexBuilder(metadata_file, bibtex_file)
        pipeline.add_step(bibtex_builder_)
        pdf_downloader_ = pdf_downloader.PdfDownloader(metadata_file, mapperclass, target_dir, list_file,
                                                       args.sample, args.maxwait, args.downloaddir)
        pipeline.add_step(pdf_downloader_)
        pipeline.run()
        logger.info('Exiting.')
    except SystemExit:
        logger.info('Exiting!')
        sys.exit(1)
    except KeyboardInterrupt:
        logger.error('Manual interruption - cancelling.')
        sys.exit(1)


if __name__ == '__main__':
    main()