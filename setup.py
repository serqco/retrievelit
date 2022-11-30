import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Setup():
    """Set up a folder and a state file named after the current target if they don't exist."""
    def __init__(self, target: str, state_file: str) -> None:
        self._target = target
        self._state_file = state_file

    def _folder_exists(self) -> bool:
        """Check if the folder for the target already exists."""
        p = Path(f'./{self._target}')
        return p.is_dir()

    def _state_file_exists(self) -> bool:
        """Check if the state file for the target already exists."""
        p = Path(self._state_file)
        return p.is_file()

    def _create_folder(self) -> None:
        """Create the folder for the target in the current directory."""
        Path(f"./{self._target}").mkdir()
        logger.info(f'Created folder {self._target}.')

    def _create_state_file(self) -> None:
        """Create a new state file containing an empty dict in the current directory."""
        with open(self._state_file, 'w') as f:
            f.write('{}')
        logger.info(f'Created new state file {self._state_file}')

    def run(self) -> None:
        """Execute the full Setup process."""
        logger.info('Setting up folder and state structure.')
        # need different behaviour if the exists or not (error vs create state file)
        if self._folder_exists():
            logger.info(f'Folder {self._target} already exists.')
            if not self._state_file_exists():
                logger.error('Folder exists but no state file found. Please delete the folder and run the downloader again.')
                raise SystemExit()
            logger.info('State file exists.')
        else:
            logger.info(f'No folder {self._target} found.')
            self._create_folder()
            self._create_state_file()
        logger.info('Setup completed.')


if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')