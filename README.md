# retrievelit: Research article corpus downloader

retrievelit consults metadata sources to find all articles in one year of a given journal or conference.  
It downloads metadata as JSON and BibTeX.  
It downloads PDFs.  
It uses a readable canonical naming rule for the PDFs (and corresponding BibTeX keys)
and avoids name collisions even across several related corpora.  

retrievelit is written in Python.

- [How to install it](#how-to-install-it)
- [How to use it](#how-to-use-it)
  - [Arguments](#arguments)
  - [Example](#example)
- [How to extend it](#how-to-extend-it)
  - [Adding a venue](#adding-a-venue)
  - [Creating a new PDF URL mapper](#creating-a-new-pdf-url-mapper)
  - [Adding a new metadata source](#adding-a-new-metadata-source)
- [TODO](#todo)

## How to install it

## How to use it
---
```bash
python main.py [-h] [--grouping {year,volume}] [--mapper MAPPER] [--metadata {dblp,crossref}] [--ieeecs] target [existing_folders ...]
```

### Arguments
| Argument | Description   | Default | Required? |
|--------|----------------------------------------------------------|--------|-----------|
| `target` | The combination of Venue and Volume/Year to be downloaded. E. g. `EMSE-35` to download all publications in Volume 35 of the Venue in `venues.py` with the key `EMSE`. This will also be the name of the folder containing the downloads. If the folder already exists, the downloader will try to resume the last state. | | Yes
| `existing folders` | Names of already existing folders containing previously downloaded publications, whose identifiers will create the namespace to generate the identifiers for the current corpus. | | No
| `--grouping`   | Whether the number after the venue describes the year or volume of the corpus. | `year` | No        |
| `--mapper` | The mapper object which will be used to get the PDF URL from the DOI. This must be the name of a class in the `doi_pdf_mappers` folder, which inherits from either ABC of [`DoiMapper`, `ResolvedDoiMapper`]. Can be lowercase or CamelCase. See [here](#how-to-extend-it) how to create your won mapper. | `HtmlParserMapper` | No
| `--metadata` | The source from which retrievelit will get the metadata and DOIs of publications in the corpus. | `dblp` | No
| `--ieeecs` | Whether DOIs pointing to `ieeexplore.ieee.org` will be rewritten to point to `computer.org` instead. | `False` | No

### Example
```bash
python main.py --grouping=volume --mapper=springermapper EMSE-35 EMSE-34 EMSE-33
```
This will download the Volume 35 of `Empirical Software Engineering` while using the class `SpringerMapper` to generate the PDF URLs. The downloader will look for existing filenames in the folders `./EMSE-34` and `./EMSE-33` to create the namespace before the generation of new filenames. Downloads and additional files will be stored in a new folder `./EMSE-35`.

## How to extend it
---

### Adding a venue
#### Why
- Adding a new venue to the downloader is necessary if you want to download a venue which isn't currently included.
- You might also want to change existing metadata of a venue if you aren't happy with the metadata (e. g. venue name) in your metadata or bibtex file.
#### How
- All venues are placed in the `venues.py` file, located in the base directory.
- To add a new venue, add a new dictionary to the `VENUES` dictionary in the file. The key will be matched to the venue string you provide as an argument when starting the downloader.
- The dictionary must contain the following fields
  - `name`: The full name of the venue. (Used in the metadata and bibtex files)
  - `type`: The type of the venue such as conference or journal. (Used in the metadata and bibtex files)
  - `metadata_sources`: A dictionary containing additional data needed for each metadata source in the form of another dict. It's not required to fill this out for all sources, but selecting a source for which required data isn't provided will lead to failure of the program.
    - `dblp`: The dblp dict must contain the following fields. To get the values, open [dblp.org](https://dblp.org), search for the venue you want to add and use the URL. (e. g. `https://dblp.org/db/journals/ese/index.html`)
      - `type`: The type of the venue, usually the second to last part of the path. (here: `journals`)
      - `acronym`: The acronym of the venue, usually the last part of the path. (here: `ese`)
#### Example
```python
'EMSE': {
        'name': 'Empirical Software Engineering',
        'type': 'journal',
        'metadata_sources': {
            'dblp': {
                'type': 'journals',
                'acronym': 'ese'
            },
        },
    },
```
---
### Creating a new PDF URL mapper
A (doi-to-pdf-url) mapper is an object which implements the `get_pdf_url` method, which takes a (resolved) DOI and returns the URL of the matching PDF for the downloader.
#### Why
- Adding a new mapper is necessary when you added a new venue from a new publisher or with a different URL schema.
- You might also want to change existing mappers if their tests fail or you notice incorrect return values.
#### How
- All mappers are located in the `doi_pdf_mappers` folder in the base directory.
- For simplicity, create a new file for each mapper. The filename is irrelevant to the program, though it should be as clear as possible for other users.
- Create a new class with a name that reflects the publisher/site and the venue if necessary. (e. g. `SpringerMapper`)
- The class has to inherit from either of the following base classes. Which one to use depends on whether your mapping function needs the "pure" DOI, or the "resolved" one (In most cases the article site of the publisher, which might contain needed internal IDs).
  - `DoiMapper` (`doi_pdf_mappers.abstract_doi_mapper.DoiMapper`)  
    Use this base class if you only need the DOI to build the PDF URL.
  - `ResolvedDoiMapper` (`doi_pdf_mappers.abstract_resolved_doi_mapper.ResolvedDoiMapper`)  
    Use this base class if you need the fully resolved DOI to build the PDF URL.
- The class has to implement the method `get_pdf_url(self, doi)` which will receive the (resolved) DOI and must return a full URL containing the relevant PDF file.
- Try to use the logging module to at least log the final URL and any relevant steps before that at the `Debug` level.
- The program will automatically pick up the new class and match it against the `--mapper` argument when starting the downloader.
#### Example
```python
import logging

from doi_pdf_mappers.abstract_doi_mapper import DoiMapper

logger = logging.getLogger(__name__)

class SpringerMapper(DoiMapper):
    def get_pdf_url(self, doi):
        url = f'https://link.springer.com/content/pdf/{doi}.pdf'
        logger.debug(f'Built PDF URL {url}')
        return url
```
---
### Adding a new metadata source
#### Why
#### How
#### Example

## TODO
---
- functionality:
  - Implement IST (Elsevier) download functionality
  - Metadata file improvements
    - combine `state.json` and `metadata.json`
    - create set schema to validate file and aid in adding new metadata sources
    - include additional information (dts of retrieval, downloader configuration, etc.)
- usability improvements:
  - check arguments before using them
  - terminate with clear error messages (instead of crashing) upon unsuitable call arguments. 
  - I am no longer convinced that the title word in citation keys and PDF filenames is useful.
    (even once it works better and ignores stopwords)
    I suggest to leave it out by default and only add it if `--longname` is given.
  - use request sessions to reduce time for consecutive requests to the same server
- tech debt reductions:
- defects:
  - --grouping=year doesn't work for ICSE (maybe all conferences), since all tracks are included in the publication API and there seems to be no way to distinguish them.
    Since there is only one conference per year, --grouping=year calls can just be mapped to volume calls.
  - 2022-09-01: TSE-2021 crashed with "No such file or directory: 'TSE-2021/El-HieTür21-$\\mathcal.pdf'"  
    Only few non-letter characters should be let through for the title word, mostly dashes.  
    For the basename, even dashes should be collapsed and 'El-Fakih' should become 'ElF', not 'El-'.
- documentation:
  - write user instructions for calls
  - write advanced-user instructions for adding venues
  - write advanced-user instructions for adding download techniques
- quality assurance:
  - add test suite
  - GitHub Continuous Integration
  - perhaps add compatibility testing with tox (and tox-docker or so)  

and more.
