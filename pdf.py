import logging
import time
import typing as tg
from pathlib import Path

import requests
from tqdm import tqdm
import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver

import utils
from exceptions.doi_pdf_mappers import PdfUrlNotFoundError
from doi_pdf_mappers.abstract_doi_mapper import DoiMapper
from doi_pdf_mappers.abstract_resolved_doi_mapper import ResolvedDoiMapper
from pipeline_step import PipelineStep

# seconds to wait between get requests (ignoring code execution time inbetween)
REQUEST_DELAY = 1

logging.getLogger("selenium").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

class PdfDownloader(PipelineStep):
    """Download the article PDFs and write the filepath to the list file."""
    def __init__(self, metadata_file: str, doi_pdf_mapper: tg.Union[DoiMapper, ResolvedDoiMapper], 
                 folder_name: str, list_file: str, dois_resolved: bool, use_selenium: bool) -> None:
        self._metadata_file = metadata_file
        self._mapper = doi_pdf_mapper
        self._folder_name = folder_name
        self._list_file = list_file
        self._dois_resolved = dois_resolved
        self._use_selenium = use_selenium
        self._metadata: tg.List = []

    def _make_get_request(self, url: str) -> requests.Response:
        """Make a GET request to url and return the response if successful."""
        logger.debug(f'GET request to {url}')
        response = requests.get(url)
        logger.debug(f'Reponse code: {response.status_code}')
        response.raise_for_status()
        #TODO catch
        time.sleep(REQUEST_DELAY)
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

    def _add_to_list(self, pdf_path: str) -> None:
        """Append the pdf filepath to the list file."""
        with open(self._list_file, 'a') as f:
            f.write(f'{pdf_path}\n')
        logger.debug(f'Added {pdf_path} to {self._list_file}.')

    def _get_pdf_with_requests(self, pdf_url: str, filename: str) -> None:
        """Use requests to download the PDFs and store it in the file."""
        pdf_data = self._get_pdf_data(pdf_url)
        self._store_pdf(pdf_data, filename)
    
    def _get_pdf_with_selenium(self, pdf_url: str, filename: str, driver: WebDriver) -> None:
        """Use Selenium to download the PDFs and store it in the file."""
        elsevier_id = pdf_url.split('/')[-2]
        # this only works for Elsevier
        # could search for newest file in folder to make it work for other sources
        download_file = Path.joinpath(Path(self._folder_name), f'1-s2.0-{elsevier_id}-main.pdf')
        logger.debug(f'Downloading PDF from URL {pdf_url} to file {download_file}.')
        driver.get(pdf_url)
        while not download_file.is_file():
            logger.debug(f"File {download_file} does not exist yet.")
            time.sleep(2)
        logger.debug(f"Finished downloading file {download_file}.")
        logger.debug(f"Renaming file to {filename}")
        download_file.rename(filename)

    def _start_driver(self) -> WebDriver:
        """Start the chrome driver, set its download directory and return it."""
        logger.info('Starting webdriver.')
        driver = uc.Chrome(version_main=107, driver_executable_path="./webdriver/chromedriver.exe")
        logger.info('Webdriver started.')
        download_path = Path.joinpath(Path(__file__).resolve().parent, self._folder_name)
        logger.debug(f'Setting PDF download target to {download_path}.')
        params = {
            "behavior": "allow",
            "downloadPath": str(download_path)
        }
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        return driver

    def run(self) -> None:
        """Run the full PDF download process."""
        self._metadata = utils.load_metadata(self._metadata_file)
        # TODO implement more robust check
        # check if there's a failure to get the PDF URL multiple times in a row
        # which might point to no access.
        access_check_count = 0
        logger.info('Starting PDF download. This may take a few seconds per PDF.')

        if self._use_selenium:
            driver = self._start_driver()

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
            # TODO change when reworking files/folder location
            filename = f"{self._folder_name}/{entry.get('identifier')}.pdf"
            
            if self._use_selenium:
                self._get_pdf_with_selenium(pdf_url, filename, driver)
            else:
                self._get_pdf_with_requests(pdf_url, filename)
            
            # this might lead to duplicate entries in the .list file
            # since it can get interrupted between appending to list file and saving the state
            # so we would append twice (can read in first and add to set if needed to combat this)
            self._add_to_list(filename)
            entry['pdf'] = True
            utils.save_metadata(self._metadata_file, self._metadata)

        if self._use_selenium:
            driver.close()


if __name__ == '__main__':
    # download_pdfs()
    logger.error('Not a standalone file. Please run the main script instead.')