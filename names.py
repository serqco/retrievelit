import logging

import utils

# from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

# def download_stopwords():
#     #TODO install in retrievelit dir, not download one
#     # download  english stopwords to location of this script
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     nltk.download('stopwords', download_dir=current_dir)

def load_stopwords():
    logger.debug('Loading stopwords.')
    with open('stopwords.txt', 'r') as f:
        stopwords_string = f.read()
    stopwords = stopwords_string.split('\n')
    logger.debug(f'Loaded stopwords {stopwords}.')
    return stopwords


def get_list_names(list_string):
    names = list_string.split('\n')
    # get identifier from path if not empty string (last new line)
    list_names = [e.split('/')[1][:-4] for e in names if e]
    logger.debug(f'Loaded names {list_names}')
    return list_names

def load_existing_names(existing_folders):
    # No need to load names for this venue-volume target,
    # since names are generated in one step, so if we get to here,
    # we want to regenerate all names anyways.
    logger.debug('Loading existing names.')

    existing_names = []
    list_files = [f'{folder}.list' for folder in existing_folders]

    for list_file in list_files:
        logger.debug(f'Reading names from file {list_file}')

        try:
            with open(list_file, 'r') as f:
                list_string = f.read()
        except FileNotFoundError:
            logger.warn(f'File {list_file} not found. Skipping.')
            continue

        list_names = get_list_names(list_string)
        existing_names.append(list_names)
        logger.debug(f'Loaded names from file {list_file}.')

    logger.debug('Finished loading existing names.')
    return existing_names

def generate_name(article, existing_names, stopwords):
    """
    """
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

    # titles such as "FACER: An API..." should lead to output "facer" (without ":")
    # while still keeping non-latin chars, so we strip of punctuation
    title = [e.lower() for e in article['title'].split()]
    title_no_stopwords = [e for e in title if e not in stopwords]
    title_part = title_no_stopwords[0].strip(":;,.#@%^&*()-_+=!?<>/\\{}[]")

    appendices = [''] + [chr(i) for i in range(97,123)]
    for e in appendices:
        full_name = f"{author_part}{year_part}{e}-{title_part}"
        logger.debug(f'Checking name {full_name} for uniqueness.')
        if full_name not in existing_names:
            logger.debug("Name is unique.")
            return full_name
        logger.debug('Name not unique. Trying new name.')
    #TODO better exception + logging
    raise Exception("Couldn't find free name!")

def add_identifiers(metadata_file, existing_folders):
    stopwords = load_stopwords()
    logger.info('Loading existing folders into namespace.')
    existing_names = load_existing_names(existing_folders)
    publications = utils.load_metadata(metadata_file)
    logger.info('Generating identifiers for publications.')
    for e in publications:
        generated_name = generate_name(e, existing_names, stopwords)
        e['identifier'] = generated_name
        existing_names.append(generated_name)
    logger.info('Identifiers generated.')
    utils.save_metadata(metadata_file, publications)

if __name__ == '__main__':
    # add_identifiers('metadata.json')
    logger.error('Not a standalone file. Please run the main script instead.')