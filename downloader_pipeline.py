import logging
import json

logger = logging.getLogger(__name__)

class DownloaderPipeline():
    def __init__(self, state_file):
        self._state_file = state_file
        self._state = {}
        self._steps = []
    
    def _load_state(self):
        logger.info('Loading state.')
        with open(self._state_file, 'r') as f:
            state = json.load(f)
        self._state = state
    
    def _save_state(self):
        logger.debug('Saving state file.')
        with open(self._state_file, 'w') as f:
            f.write(json.dumps(self._state))
        logger.debug('Finished saving state.')
    
    def add_step(self, step):
        self._steps.append(step)
    
    def run(self):
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
                
    
    