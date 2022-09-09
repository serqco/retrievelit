import logging

# because of the code in 'doi_pdf_mappers.__init__.py', this loads in all modules in that package
from doi_pdf_mappers import *

logger = logging.getLogger(__name__)

def get_mapper(name):
    logger.debug('Trying to find mapper class for provided mapper name.')
    # all classes in that folder which implement the Mapper ABC.
    subclasses = abstract_doi_mapper.DoiMapper.__subclasses__()
    subclasses += abstract_resolved_doi_mapper.ResolvedDoiMapper.__subclasses__()
    logger.debug(f'Loaded subclasses of Mapper ABCs: {subclasses}.')
    for sc in subclasses:
        if sc.__name__ == name or sc.__name__.lower() == name:
            logger.debug(f'Matching class found: {sc}.')
            return sc()
    logger.error(f"No mapping module found for string {name}. Please check your spelling and make sure a file exists in the 'doi_pdf_mappers' folder, which inherits from one of the Mapper classes.")
    