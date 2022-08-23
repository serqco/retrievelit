import json
import os
import nltk
import logging
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

def download_stopwords():
    #TODO install in retrievelit dir, not download one
    #TODO maybe just add the english.txt file to git (make sure this is legally okay)
    # download  english stopwords to location of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nltk.download('stopwords', download_dir=current_dir)

def load_existing_names():
    #TODO implement loading names from multiple directories
        # get all .list files with prefix of provided args
            # (we can use the .list file with pdf names since we only want to use correctly downloaded directories anyways, if file not found -> something went wrong)
        # parse out all identifiers
            # TODO -> is this the best source for these? (is this stable?)
    # ignore if name list exists in this directory?
    existing_names = ['AbiShaBas21-facer', 'AbiShaBas21a-facer', 'AbiShaBas21b-facer']
    return existing_names

def generate_name(article, existing_names):
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
    title_no_stopwords = [e for e in title if e not in stopwords.words('english')]
    title_part = title_no_stopwords[0].strip(":;,.#@%^&*()-_+=!?<>/\\{}[]")

    appendices = [''] + [chr(i) for i in range(97,123)]
    for e in appendices:
        full_name = f"{author_part}{year_part}{e}-{title_part}"
        if full_name not in existing_names:
            logger.debug(f"generated name: {full_name}")
            return full_name
    #TODO better exception
    raise Exception("Couldn't find free name!")

def add_identifiers(metadata_file):
    #TODO log
    # download_stopwords()
    logger.info('Loading existing folders into namespace.')
    existing_names = load_existing_names()
    logger.info('Reading metadata file.')
        #TODO put write in function
    with open(metadata_file, 'r') as f:
        #TODO file not found
        publications = json.loads(f.read())
    logger.info('Metadata loaded.')
    logger.info('Generating identifiers for publications.')
    for e in publications:
        generated_name = generate_name(e, existing_names)
        e['identifier'] = generated_name
        existing_names.append(generated_name)
    logger.info('Identifiers generated.')
    logger.info('Saving to metadata file.')
    with open(metadata_file, 'w') as f:
        f.write(json.dumps(publications))
    logger.info(f'Identifiers saved to file {metadata_file}')

if __name__ == '__main__':
    add_identifiers('metadata.json')
    