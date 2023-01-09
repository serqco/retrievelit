import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Setup():
    """Set up a folder and a state file named after the current target if they don't exist."""
    def __init__(self, metadata_dir: Path, state_file: Path) -> None:
        self._metadata_dir = metadata_dir
        self._state_file = state_file

    def _create_state_file(self) -> None:
        """Create a new state file containing an empty dict in the target directory."""
        with open(self._state_file, 'w') as f:
            f.write('{}')
        logger.info(f'Created new state file at {self._state_file}.')

    def run(self) -> None:
        """Execute the full Setup process."""
        logger.info('Setting up folder and state structure.')
        logger.info(f"Creating target and metadata folder at {self._metadata_dir} if they don't exist.")
        self._metadata_dir.mkdir(exist_ok=True, parents=True)
        if not self._state_file.is_file():
            logger.info('Creating state file.')
            self._create_state_file()
        else:
            logger.info('State file already exists.')
        logger.info('Setup completed.')


if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')