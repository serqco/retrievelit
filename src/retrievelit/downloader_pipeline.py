import logging
import json
import typing as tg
from pathlib import Path

from retrievelit.pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

class DownloaderPipeline():
    """Class to define and execute the pipeline of the downloader."""
    # TODO add proper docstring for public methods.
    def __init__(self, metadata_file: Path) -> None:
        self._metadata_file = metadata_file
        self._state: tg.Dict = {}
        self._steps: tg.List = []
    
    def _load_state(self) -> None:
        """Load the state from the metadata file."""
        logger.info('Loading state.')
        with open(self._metadata_file, 'r', encoding="utf8") as f:
            metadata = json.load(f)
        try:
            self._state = metadata['state']
        except KeyError:
            logger.error(f"Metadata file {self._metadata_file} does not contain state.")
            raise SystemExit()
    
    def _save_state(self) -> None:
        """Save the current state to the metadata file."""
        logger.debug('Saving state to metadata file.')
        with open(self._metadata_file, 'r', encoding="utf8") as f:
            metadata = json.load(f)
        metadata['state'] = self._state
        with open(self._metadata_file, 'w', encoding="utf8") as f:
            f.write(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))
        logger.debug('Finished saving state.')
    
    def add_step(self, step: PipelineStep) -> None:
        """Add a PipelineStep to the pipeline."""
        self._steps.append(step)
    
    def run(self) -> None:
        """Execute the pipeline by running each step and saving state inbetween."""
        self._load_state()
        
        for step in self._steps:
            step_name = type(step).__name__ # = classname
            if self._state.get(step_name):
                logger.info(f'Step {step_name} already done. Skipping.')
            else:
                logger.info(f'Starting step {step_name}.')
                step.run()
                logger.info(f'Finished step {step_name}.')
                self._state[step_name] = True
                self._save_state()
                
    
    