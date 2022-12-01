import logging
import json
import typing as tg
from pipeline_step import PipelineStep

logger = logging.getLogger(__name__)

class DownloaderPipeline():
    """Class to define and execute the pipeline of the downloader."""
    # TODO add proper docstring for public methods.
    def __init__(self, state_file: str) -> None:
        self._state_file = state_file
        self._state: tg.Dict = {}
        self._steps: tg.List = []
    
    def _load_state(self) -> None:
        """Open the state file and load its contents."""
        logger.info('Loading state.')
        with open(self._state_file, 'r') as f:
            state = json.load(f)
        self._state = state
    
    def _save_state(self) -> None:
        """Save the current state to the state file."""
        logger.debug('Saving state file.')
        with open(self._state_file, 'w') as f:
            f.write(json.dumps(self._state))
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
                
    
    