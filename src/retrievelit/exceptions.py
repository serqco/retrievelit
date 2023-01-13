class PdfUrlNotFoundError(Exception):
    """A mapper could not find a corresponding PDF download URL for a DOI."""
    pass

class NoEntriesReceivedError(Exception):
    """The Metadatasource did not return any entries for the current target and configuration."""
    pass