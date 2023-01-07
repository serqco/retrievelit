import logging
import typing as tg

from retrievelit.doi_pdf_mappers import *  # make sure all mappers have been loaded
from retrievelit.doi_pdf_mappers import abstract_doi_mapper, abstract_resolved_doi_mapper

logger = logging.getLogger(__name__)

def get_mapper(name: str) -> tg.Union[abstract_doi_mapper.DoiMapper,
                                      abstract_resolved_doi_mapper.ResolvedDoiMapper]:
    """Return an instance of the mapper class specified in `name`, if possible."""
    logger.debug('Trying to find mapper class for provided mapper name.')
    # all classes in that folder which implement the Mapper ABC.
    fullname = f"{name}Mapper"
    for sc in mapper_classes():
        if sc.__name__ == fullname:
            logger.debug(f'Matching class found: {sc}.')
            return sc()
    logger.error(f"No mapper class {fullname} found for mapper name {name}. "
                 "Make sure the class exists under 'doi_pdf_mappers' and inherits from a Mapper baseclass.")
    raise SystemExit()


def mapper_classes() -> tg.Sequence[tg.Type]:
    """Return all subclasses of DoiMapper and ResolvedDoiMapper."""
    return (abstract_doi_mapper.DoiMapper.__subclasses__() +
            abstract_resolved_doi_mapper.ResolvedDoiMapper.__subclasses__())


def mapper_names() -> tg.Sequence[str]:
    """Return the names of all classes in mapper_classes(), without the `Mapper` substring."""
    logger.debug(f"{len(mapper_classes())} mapper classes")
    return [cls.__name__.replace("Mapper", "") for cls in mapper_classes()]
