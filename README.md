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
  - [Notes](#notes)
- [How to extend it](#how-to-extend-it)
  - [Adding a venue](#adding-a-venue)
  - [Creating a new PDF URL mapper](#creating-a-new-pdf-url-mapper)
  - [Adding a new metadata source](#adding-a-new-metadata-source)
- [TODO](#todo)

## How to install it
- Clone the repository on your local machine.
- Install the package by running `pip install .` in the root directory.
### Development Installation
To work on this package you have to install it in editable mode. This will allow you to run the package as usual while reflecting all changes you make to the source code, as well as run the test suite.

- Clone the repository on your local machine.
- Install the package in editable mode to link it to the local files by running `pip install -e .[tests]` in the root directory.

## How to use it

1. Make sure your default webbrowser is configured to download PDFs (as opposed to showing them
   in the browser or asking what to do).
2. Visit the publisher's web page, confirm any cookie questions, log in (if needed).
3. Now call `retrievelit` as described below.  
   Depending on how your browser is configured with respect to using tabs, this may open a new tab
   for each downloaded file. You may close older tabs (not the current one!) at any time.  
   `retrievelit` assumes your browser places the downloads in directory `Downloads` in your
   home directory. If that is not the case, supply the full path to the download directory
   as `--downloaddir=/path/to/mydownloaddir` etc.

```bash
retrievelit [-h] [--grouping {year,volume}] [--mapper MAPPER] [--sample N] target [existing_folders ...]
```
There are more options than the above. Use `-h` to learn about them.
We explain the use by example:

### Example
```bash
retrievelit --grouping=volume --mapper=Springer EMSE-25 EMSE-24 EMSE-23
```
This will download Volume 25 (which is the volume of the year 2020) of `Empirical Software Engineering` 
and use class `SpringerMapper` to map DOIs to PDF URLs.
The downloader will consider existing filenames in the folders `./EMSE-34` and `./EMSE-33` and will avoid name duplicates. 
The downloaded PDFs will be stored in a new folder `./EMSE-25`.
In the folder `./EMSE-25/metadata` the following files will be created:
- `EMSE-25-dblp.json`.
  - Contains the corpus metadata as well as information about the downloader run such as the run configuration and the current state in a JSON object.
- `EMSE-25-dblp.bib`.
  - Contains the corpus metadata in the BibTeX format.
- `EMSE-25-dblp.list`.
  - Contains one filepath per line for each of the PDFs.

Result directories are always created in the working directory.  
For retrieving by year, use `--grouping=year`, which is also the default (so there is no need to actually use it).    
Some conferences will need `--grouping=volume` although the number supplied is a year.  
Use something like `--sample=50` if you want to download only 50 randomly chosen articles instead of
the entire volume. Use `--sample=1` for testing whether a download works at all; delete the resulting
directory before the next try.  
If `retrievelit` hangs during PDF download, this may be because it is expecting the files to appear
in a different place than they actually do. Use `--downloaddir=...` to fix this.  
DBLP is the only metadata source so far; `--metadata=crossref` is not yet implemented.  
The meaning of 'EMSE' and the other venue names are defined in `venues.py`.  

### Notes

#### Downloading ICSE Technical Track with dblp.org
- Due to limitations of the dblp publication API, downloading the Technical Track of ICSE is only possible when using the option `--grouping=volume` and supplying the publication year as the volume number.
- Example to download the technical track of ICSE 2021: `retrievelit --grouping=volume --mapper=ComputerOrgConf ICSE-2021`
- All downloads of ICSE using `--grouping=year` will be mapped to `--grouping=volume` while keeping all other options the same.

## How to extend it

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

### Creating a new PDF URL mapper
A (doi-to-pdf-url) mapper is an object which implements the `get_pdf_url` method, 
which takes a DOI and returns the URL of the matching PDF for the downloader.
It can potentially also implement the `get_pdfdescriptor` method, which returns a pair of
such a PDF URL and a PDF filename. 

#### Why
Adding a new mapper is necessary when you added a new venue from a new publisher or with a different URL schema.

Why the two different types of mappers?
If the `get_pdfdescriptor` method exists, the PDFs will not be retrieved by direct GET requests,
but rather the retrieval will be delegated to the browser, which (if it is configured correctly)
will place the PDF in its download folder, where retrievelit will pick it up under the given filename.

This process is more suitable if the publisher's server is robot averse.
Direct GET requests are more robust and stable from a purely technical point of view,
however, the browser-based approach is more stable in practice, because some publishers
(e.g. Elsevier) will not let you download with direct GET requests at all and others
(e.g. ACM) will quickly block your IP if you do this more than a very few times. 
Beware!


#### How
- All mappers are located in the `doi_pdf_mappers` folder in the base directory.
- For simplicity, create a new file for each mapper. The filename is irrelevant to the program, though it should be as clear as possible for other users.
- Create a new class with a name that reflects the publisher/site and the venue if necessary.
  It must end in `Mapper`, e. g. `SpringerMapper`.
- The class has to inherit from either of the following base classes. 
  Which one to use depends on whether your mapping function needs the "pure" DOI only or a "resolved" one.
  - `DoiMapper` (`doi_pdf_mappers.abstract_doi_mapper.DoiMapper`)  
    Use this base class if you only need the DOI to build the PDF URL.
  - `ResolvedDoiMapper` (`doi_pdf_mappers.abstract_resolved_doi_mapper.ResolvedDoiMapper`)  
    Use this base class if some kind of resolving the DOI is required to build the PDF URL.
- The class has to implement the method `get_pdf_url(self, doi)` which will receive the (resolved) DOI and must return a full URL containing the relevant PDF file.
- Use the logging module to log the final URL and any relevant steps before that at the `Debug` level.
- The program will automatically pick up the new class and match its name against the `--mapper` argument when starting the downloader.
- After verifying your mapper works as expected, please add a test for it by completing the following steps.
  - Go to the `test_mappers.py` file in the `tests` directory.
  - Import your new Mapper class.
  - Add a tuple containing the classname, as well as a string containing a (resolved) DOI which currently works with the mapper to the `inputs` list.
  - When running the test suite, this test will confirm whether the mapper still returns a working URL containing PDF data.
- Study `SpringerMapper` (in `doi_pdf_mappers/springer.py`) as a simple example.

### Adding a new metadata source
#### Why
#### How
#### Example

## TODO
- functionality:
  - how to download different ICSE tracks?
  - add timestamps of metadata retrieval, pdf download, etc. to metadata file?
- tech debt reductions:
  - remove most logger.debug() calls
- defects:
- documentation:
- quality assurance:
  - add a system test  (a CI is too difficult)
