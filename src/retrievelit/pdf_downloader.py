import logging
import random
import time
import typing as tg
import webbrowser
from pathlib import Path

from tqdm import tqdm

from retrievelit import utils
from retrievelit.exceptions import PdfUrlNotFoundError
from retrievelit.doi_pdf_mappers.base import DoiMapper, PDFDescriptor
from retrievelit.pipeline_step import PipelineStep

# seconds to wait between get requests (ignoring code execution time inbetween)
REQUEST_DELAY = 1

logger = logging.getLogger(__name__)

class PdfDownloader(PipelineStep):
    """Download the article PDFs and write the filepath to the list file."""
    def __init__(self, metadata_file: Path, doi_pdf_mapper: DoiMapper, 
                 target_dir: Path, list_file: Path, 
                 samplesize: tg.Optional[int], maxwait: int, downloaddir: str):
        self._metadata_file = metadata_file
        self._mapper = doi_pdf_mapper
        self._target_dir = target_dir
        self._list_file = list_file
        self._samplesize = samplesize
        self._maxwait = max(4, maxwait)
        self._downloaddir = downloaddir
        self._metadata: tg.List = []
        self._use_webbrowser = self._webbrowser_required()

    def _get_sample(self, samplesize: tg.Optional[int], metadata: tg.Mapping[str, tg.Any]) -> tg.Mapping[str, tg.Any]:
        if samplesize is None:
            return metadata  # no sampling, use all data (the default case)
        if samplesize == 0:
            return dict()  # empty sample
        return random.sample(population=metadata, k=min(samplesize, len(metadata)))

    def _webbrowser_required(self) -> bool:
        """Check if the target requires download through webbrowser, based on the selected mapper."""
        if getattr(self._mapper, 'get_pdfdescriptor'):
            logger.debug(f"Mapper suggests download by the webbrowser module.")
            return True
        else:
            logger.debug(f"Target will be downloaded by direct GET requests.")
            return False

    def _get_pdf_data(self, pdf_url: str) -> bytes:
        r = utils.make_get_request(pdf_url, REQUEST_DELAY)
        content_type = r.headers.get('Content-Type')
        if content_type is None or 'application/pdf' not in content_type:
            logger.error("Resonse from PDF URL didn't contain PDF data. This might be because your IP doesn't have access. Check the logs to see the URL and manually open it to debug.")
            raise SystemExit()
        return r.content

    def _store_pdf(self, pdf_data: bytes, pdf_path: Path) -> None:
        """Write pdf_data to a file."""
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        logger.debug(f'Wrote PDF to file {pdf_path}')
    
    def _download_pdf_with_requests(self, pdf_url: str, pdf_path: Path) -> None:
        """Use requests to download the PDF and store it in `filename`."""
        pdf_data = self._get_pdf_data(pdf_url)
        self._store_pdf(pdf_data, pdf_path)
    
    def _download_pdf_with_webbrowser(self, pdfdescriptor: PDFDescriptor, pdf_targetfilename: Path,
                                      download_dir: Path) -> None:
        """Use the webbrowser module to download the PDF and store it in `filename`."""
        def is_download_finished(file: Path) -> bool:
            """Check if the PDF file download can be assumed to be complete."""
            size_old = file.stat().st_size
            time.sleep(2)
            size_new = file.stat().st_size
            logger.debug(f"Size of file {str(file)}: old: {size_old}, new: {size_new}.")
            return size_old == size_new

        pdf_file = Path.joinpath(download_dir, pdfdescriptor.filename)
        
        logger.debug(f"Opening {pdfdescriptor.download_url} in browser.")
        webbrowser.open(pdfdescriptor.download_url, 0)
        # keep this order and no parantheses to take advantage of lazy evaluation:
        while not pdf_file.is_file() or not is_download_finished(pdf_file):
            logger.debug(f"Download of file {pdf_file} is not finished.")
            time.sleep(2)

        logger.debug(f"Finished downloading file {pdf_file}.")
        new_path = Path.joinpath(Path(), pdf_targetfilename)
        logger.debug(f"Moving and renaming file to {new_path}.")
        pdf_file.rename(new_path)
        
    def _add_to_list(self, pdf_path: Path) -> None:
        """Append the pdf filepath to the list file."""
        with open(self._list_file, 'a', encoding='utf8') as f:
            f.write(f'{pdf_path.as_posix()}\n')
        logger.debug(f'Added {pdf_path} to {self._list_file}.')

    def run(self) -> None:
        """Run the full PDF download process."""
        self._metadata = utils.load_metadata(self._metadata_file)

        logger.info('Starting PDF download. This may take a while for each PDF.')

        for entry in tqdm(self._get_sample(self._samplesize, self._metadata)):

            if entry.get('pdf'):
                logger.debug(f'PDF already downloaded for entry {entry}. Skipping.')
                continue

            # get doi parameter from entry
            doi_parameter = entry.get('doi')
            if not doi_parameter:
                logger.warning(f"No DOI provided in entry {entry}. Skipping.")
                continue
            
            # get pdf url from mapper
            try:
                if self._use_webbrowser:
                    pdfdescriptor = self._mapper.get_pdfdescriptor(doi_parameter)
                else:
                    pdf_dl_url = self._mapper.get_pdf_url(doi_parameter)
            except PdfUrlNotFoundError as e:
                logger.warning(repr(e))
                logger.warning(f"No pdf URL found for DOI {doi_parameter}. Skipping. If this reoccurs, check if you have access to this publication.")
                continue
            
            # generate filename
            if not entry.get('identifier'):
                logger.warning(f'No identifier found in entry {entry}. Skipping.')
                continue
            pdf_path = Path.joinpath(self._target_dir, f"{entry.get('identifier')}.pdf")
            
            if self._use_webbrowser:
                self._download_pdf_with_webbrowser(pdfdescriptor, pdf_path, self._downloaddir)
            else:
                self._download_pdf_with_requests(pdf_dl_url, pdf_path)
            time.sleep(random.uniform(0.25*self._maxwait, self._maxwait))

            # this might lead to duplicate entries in the .list file
            # since it can get interrupted between appending to list file and saving the state
            # so we would append twice (can read in first and add to set if needed to combat this)
            self._add_to_list(pdf_path)
            entry['pdf'] = True
            utils.save_metadata(self._metadata_file, self._metadata)
