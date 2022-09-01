import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def folder_exists(name):
    p = Path(f'./{name}')
    return p.is_dir()

def state_file_exists(state_file):
    p = Path(state_file)
    return p.is_file()

def create_folder(name):
    Path(f"./{name}").mkdir()
    logger.info(f'Created folder {name}.')

def create_state_file(state_file):
    contents = {
        'metadata_download': False,
        'identifier': False,
        'bibtex': False,
        'pdf': False,
    }
    with open(state_file, 'w') as f:
        f.write(json.dumps(contents))
    logger.info(f'Created new state file {state_file}')

#TODO rename function
def main(name, state_file):
    logger.info('Setting up folder and state structure.')
    # need different behaviour if the exists or not (error vs create state file)
    if folder_exists(name):
        logger.info(f'Folder {name} already exists.')
        if not state_file_exists(state_file):
            logger.error('No state file found.')
            #TODO better exception/create custom/better hints
            # -> either target is fully downloaded or no steps were completed
            # TODO add CLI option to force restart of a existing target folder (delete contents and start from zero)
            raise Exception('no state file found. Force full restart of this download with flag.')
        logger.info('State file found, resuming state.')
    else:
        logger.info(f'No folder {name} found.')
        create_folder(name)
        create_state_file(state_file)
    logger.info('Setup completed.')


if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')