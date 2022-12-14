import logging
import time
import typing as tg
import webbrowser
from pathlib import Path

import requests
from tqdm import tqdm

import utils
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError
from doi_pdf_mappers.abstract_doi_mapper import DoiMapper
from doi_pdf_mappers.abstract_resolved_doi_mapper import ResolvedDoiMapper
from doi_pdf_mappers.elsevier import ElsevierMapper
from pipeline_step import PipelineStep

# seconds to wait between get requests (ignoring code execution time inbetween)
REQUEST_DELAY = 1

logger = logging.getLogger(__name__)

class PdfDownloader(PipelineStep):
    """Download the article PDFs and write the filepath to the list file."""
    def __init__(self, metadata_file: str, doi_pdf_mapper: tg.Union[DoiMapper, ResolvedDoiMapper], 
                 folder_name: str, list_file: str, dois_resolved: bool) -> None:
        self._metadata_file = metadata_file
        self._mapper = doi_pdf_mapper
        self._folder_name = folder_name
        self._list_file = list_file
        self._dois_resolved = dois_resolved
        self._metadata: tg.List = []
        self._use_webbrowser = self._webbrowser_required()

    def _webbrowser_required(self) -> bool:
        """Check if the target requires download through webbrowser, based on the selected mapper."""
        if isinstance(self._mapper, ElsevierMapper):
            logger.debug(f"Target requires download by the webbrowser module.")
            return True
        else:
            logger.debug(f"Target can be downloaded by requests.")
            return False

    def _make_get_request(self, url: str) -> requests.Response:
        """Make a GET request to url and return the response if successful."""
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        #TODO catch
        return response

    def _get_pdf_data(self, pdf_url: str) -> bytes:
        r = self._make_get_request(pdf_url)
        content_type = r.headers.get('Content-Type')
        if content_type is None or 'application/pdf' not in content_type:
            logger.error("Resonse from PDF URL didn't contain PDF data. This might be because your IP doesn't have access. Check the logs to see the URL and manually open it to debug.")
            raise SystemExit()
        return r.content

    def _store_pdf(self, pdf_data: bytes, filename: str) -> None:
        """Write pdf_data to a file."""
        with open(filename, 'wb') as f:
            f.write(pdf_data)
        logger.debug(f'Wrote PDF to file {filename}')
    
    def _download_pdf_with_requests(self, pdf_url: str, filename: str) -> None:
        """Use requests to download the PDF and store it in `filename`."""
        pdf_data = self._get_pdf_data(pdf_url)
        self._store_pdf(pdf_data, filename)
    
    def _download_pdf_with_webbrowser(self, pdf_url: str, filename: str,
                                      download_dir: Path, root_dir: Path) -> None:
        """Use the webbrowser module to download the PDF and store it in `filename`."""
        def is_download_finished(file: Path) -> bool:
            """Check if the PDF file download can be assumed to be complete."""
            size_old = file.stat().st_size
            time.sleep(2)
            size_new = file.stat().st_size
            logger.debug(f"Size of file {str(file)}: old: {size_old}, new: {size_new}.")
            return size_old == size_new

        elsevier_id = pdf_url.split('/')[-2]
        # filename of all IST (Elsevier) downloads from all tested browsers
        download_filename = f'1-s2.0-{elsevier_id}-main.pdf'
        pdf_file = Path.joinpath(download_dir, download_filename)
        
        logger.debug(f"Opening {pdf_url} in browser.")
        webbrowser.open(pdf_url, 0)
        # keep this order and no parantheses to take advantage of lazy evaluation
        while not pdf_file.is_file() or not is_download_finished(pdf_file):
            logger.debug(f"Download of file {pdf_file} is not finished.")
            time.sleep(2)

        logger.debug(f"Finished downloading file {pdf_file}.")
        new_path = Path.joinpath(root_dir, filename)
        logger.debug(f"Moving and renaming file to {new_path}.")
        pdf_file.rename(new_path)
        
    def _add_to_list(self, pdf_path: str) -> None:
        """Append the pdf filepath to the list file."""
        with open(self._list_file, 'a') as f:
            f.write(f'{pdf_path}\n')
        logger.debug(f'Added {pdf_path} to {self._list_file}.')

    def run(self) -> None:
        """Run the full PDF download process."""
        self._metadata = utils.load_metadata(self._metadata_file)

        if self._use_webbrowser:
            download_dir = Path.joinpath(Path.home(), 'Downloads')
            logger.info(f"Assuming browser downloads in {str(download_dir)}."
                        " If this is incorrect, please overwrite `download_dir` in `PdfDownloader` with the correct value.")
            # TODO change when reworking folder structure 
            root_dir = Path(__file__).resolve().parent
            logger.debug(f"Assuming target folder location at {root_dir}.")

        # TODO implement more robust check
        # check if there's a failure to get the PDF URL multiple times in a row
        # which might point to no access.
        access_check_count = 0
        logger.info('Starting PDF download. This may take a few seconds per PDF.')

        for entry in tqdm(self._metadata):
            if access_check_count > 1:
                logger.error('Failed to get PDF URL too often - Aborting run. Please check if you have access to the publications, if you need to enable the --ieeecs flag, or if the the metadata-file is corrupted and try again.')
                raise SystemExit()

            if entry.get('pdf'):
                logger.debug(f'PDF already downloaded for entry {entry}. Skipping.')
                continue

            # get doi parameter from entry
            doi_parameter = entry.get('resolved_doi') if self._dois_resolved else entry.get('doi')
            if not doi_parameter:
                logger.warning(f"No {'resolved ' if self._dois_resolved else ''}DOI provided in entry {entry}. Skipping.")
                continue
            
            # get pdf url from mapper
            try:
                pdf_url = self._mapper.get_pdf_url(doi_parameter)
            except PdfUrlNotFoundError as e:
                logger.warning(repr(e))
                logger.warning(f"No pdf URL found for [resolved] DOI {doi_parameter}. Skipping. If this reoccurs, check if you have access to this publication.")
                access_check_count += 1
                continue
            
            # generate filename
            if not entry.get('identifier'):
                logger.warning(f'No identifier found in entry {entry}. Skipping.')
                continue
            # TODO change when reworking folder structure
            filename = f"{self._folder_name}/{entry.get('identifier')}.pdf"
            
            if self._use_webbrowser:
                self._download_pdf_with_webbrowser(pdf_url, filename, download_dir, root_dir)
            else:
                self._download_pdf_with_requests(pdf_url, filename)
            time.sleep(REQUEST_DELAY)

            # this might lead to duplicate entries in the .list file
            # since it can get interrupted between appending to list file and saving the state
            # so we would append twice (can read in first and add to set if needed to combat this)
            self._add_to_list(filename)
            entry['pdf'] = True
            utils.save_metadata(self._metadata_file, self._metadata)


if __name__ == '__main__':
    # download_pdfs()
    logger.error('Not a standalone file. Please run the main script instead.')