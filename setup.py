import logging
import requests
import zipfile
import io
from pathlib import Path

logger = logging.getLogger(__name__)

class Setup():
    """Setup the needed files and structure for the downloader.
    
    Set up a folder and a state file named after the current target if they don't exist.
    If the download target requires Selenium, make sure the driver exists in the correct
    directory, otherwise install it.
    """
    def __init__(self, target: str, state_file: str, use_selenium: bool) -> None:
        self._target = target
        self._state_file = state_file
        self._use_selenium = use_selenium

    def _target_folder_exists(self) -> bool:
        """Check if the folder for the target already exists."""
        p = Path(f'./{self._target}')
        return p.is_dir()

    def _state_file_exists(self) -> bool:
        """Check if the state file for the target already exists."""
        p = Path(self._state_file)
        return p.is_file()

    def _create_target_folder(self) -> None:
        """Create the folder for the target in the current directory."""
        Path(f"./{self._target}").mkdir()
        logger.info(f'Created folder {self._target}.')

    def _create_state_file(self) -> None:
        """Create a new state file containing an empty dict in the current directory."""
        with open(self._state_file, 'w') as f:
            f.write('{}')
        logger.info(f'Created new state file {self._state_file}')

    def _create_webdriver_folder(self) -> None:
        logger.info('Creating webdriver folder if it does not exist.')
        Path("./webdriver").mkdir(exist_ok=True)
    
    def _driver_exists(self) -> bool:
        """Check if the webdriver executable exists in the webdriver directory."""
        return Path("./webdriver/chromedriver.exe").is_file()

    def _install_driver(self) -> None:
        """Install the chrome webdriver in the webdriver directory."""
        # TODO change to path independent of this files location
        self._create_webdriver_folder()
        r = requests.get('https://chromedriver.storage.googleapis.com/107.0.5304.62/chromedriver_win32.zip')
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./webdriver")


    def run(self) -> None:
        """Execute the full Setup process."""
        logger.info('Setting up folder and state structure.')
        # need different behaviour if the exists or not (error vs create state file)
        if self._target_folder_exists():
            logger.info(f'Folder {self._target} already exists.')
            if not self._state_file_exists():
                logger.error('Folder exists but no state file found. Please delete the folder and run the downloader again.')
                raise SystemExit()
            logger.info('State file exists.')
        else:
            logger.info(f'No folder {self._target} found.')
            self._create_target_folder()
            self._create_state_file()
        logger.info('Setup completed.')

        if self._use_selenium:
            if self._driver_exists():
                logger.info('Webdriver found. Skipping installation.')
            else:
                logger.info('No Webdriver file found. Installing.')
                self._install_driver()

if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')