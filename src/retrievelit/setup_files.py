import logging
import json
from pathlib import Path
import typing as tg

logger = logging.getLogger(__name__)

class Setup():
    """Set up a folder and a metadata file named after the current target if they don't exist."""
    def __init__(self, metadata_dir: Path, metadata_file: Path, run_config: tg.Dict) -> None:
        self._metadata_dir = metadata_dir
        self._metadata_file = metadata_file
        self._run_config = run_config

    def _create_metadata_file(self) -> None:
        """Create a new metadata file in the target directory."""
        content = {
            "run_configuration": self._run_config,
            "state": {},
            "corpus_metadata": []
        }
        with open(self._metadata_file, 'w', encoding="utf8") as f:
            f.write(json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True))
        logger.info(f'Created new metadata file at {self._metadata_file}.')

    def run(self) -> None:
        """Execute the full Setup process."""
        logger.info('Setting up folder and metadata structure.')
        logger.info(f"Creating target and metadata folder at {self._metadata_dir} if they don't exist.")
        self._metadata_dir.mkdir(exist_ok=True, parents=True)
        if not self._metadata_file.is_file():
            logger.info('Creating metadata file.')
            self._create_metadata_file()
        else:
            logger.info('Metadata file already exists.')
        logger.info('Setup completed.')


if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')