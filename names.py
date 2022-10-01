import logging

import utils
from pipeline_step import PipelineStep

# from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

class NameGenerator(PipelineStep):
    """
    Create filenames from authornames: Full lastname if there is only 1 author,
    otherwise three lastname starting letters of up to 3 authors.
    If append_keyword is given, add the first non-stopword title word. 
    """
    def __init__(self, metadata_file, existing_folders, append_keyword=False):
        self._metadata_file = metadata_file
        self._existing_folders = existing_folders
        self._existing_names = []
        self._append_keyword = append_keyword
        self._stopwords = []
        self._metadata = []
    
    def _load_stopwords(self):
        logger.debug('Loading stopwords.')
        with open('stopwords.txt', 'r') as f:
            stopwords_string = f.read()
        self._stopwords = stopwords_string.split('\n')
        logger.debug(f'Loaded stopwords {self._stopwords}.')

    def _get_names_from_list(self, list_string):
        names = list_string.split('\n')
        # get identifier from path if not empty string (last new line)
        list_names = [e.split('/')[1][:-4] for e in names if e]
        logger.debug(f'Loaded names {list_names}')
        return list_names

    def _load_existing_names(self):
        # No need to load names for this venue-volume target,
        # since names are generated in one step, so if we get to here,
        # we want to regenerate all names anyways.
        logger.debug('Loading existing names.')
        list_files = [f'{folder}.list' for folder in self._existing_folders]

        for list_file in list_files:
            logger.debug(f'Reading names from file {list_file}')

            try:
                with open(list_file, 'r') as f:
                    list_string = f.read()
            except FileNotFoundError:
                logger.warn(f'File {list_file} not found. Skipping.')
                continue

            list_names = self._get_names_from_list(list_string)
            self._existing_names.append(list_names)
            logger.debug(f'Loaded names from file {list_file}.')
        logger.debug('Finished loading existing names.')

    def _generate_name(self, article):
        # assume surnames such as "van Klaassen" should lead to output "Kla",
        # while "Mueller-Birn" should lead to "Mue"
        # so seperate by whitespace and take last word

        # first 3 letters of last name of first 3 authors
        # if 1 author, full first word of last name
        author_part = ""
        surnames = [name.split()[-1] for name in article['authors'][:3]]
        if len(surnames) == 1:
            author_part += surnames[0]
        if len(surnames) > 1:
            clipped_surnames = [surname[:3] for surname in surnames]
            author_part += ''.join(clipped_surnames)
        
        year_part = article['year'][-2:]

        if self._append_keyword:
            # titles such as "FACER: An API..." should lead to output "facer" (without ":")
            # while still keeping non-latin chars, so we strip of punctuation
            title = [e.lower() for e in article['title'].split()]
            title_no_stopwords = [e for e in title if e not in self._stopwords]
            title_part = "-" + title_no_stopwords[0].strip(":;,.#@%^&*()-_+=!?<>/\\{}[]")
        else:
            title_part = ""
        appendices = [''] + [chr(i) for i in range(97,123)]
        for e in appendices:
            full_name = f"{author_part}{year_part}{e}{title_part}"
            logger.debug(f'Checking name {full_name} for uniqueness.')
            if full_name not in self._existing_names:
                logger.debug("Name is unique.")
                return full_name
            logger.debug('Name not unique. Trying new name.')
        #TODO better exception + logging
        raise Exception("Couldn't find free name!")

    def run(self):
        if self._append_keyword:
            self._load_stopwords()
        logger.debug('Loading existing folders into namespace.')
        self._load_existing_names()
        self._metadata = utils.load_metadata(self._metadata_file)
        logger.debug('Generating identifiers for publications.')
        for e in self._metadata:
            generated_name = self._generate_name(e)
            e['identifier'] = generated_name
            self._existing_names.append(generated_name)
        logger.debug('Identifiers generated.')
        utils.save_metadata(self._metadata_file, self._metadata)

if __name__ == '__main__':
    logger.error('Not a standalone file. Please run the main script instead.')