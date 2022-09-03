# retrievelit: Research article corpus downloader

retrievelit consults metadata sources to find all articles in one year of a given journal or conference.  
It downloads metadata as JSON and BibTeX.  
It downloads PDFs.  
It uses a readable canonical naming rule for the PDFs (and corresponding BibTeX keys)
and avoids name collisions even across several related corpora.  

retrievelit is written in Python.

## How to use it

...


## How to extend it

...


## TODO

- functionality:
  - ...
- usability improvements:
  - check arguments before using them
  - terminate with clear error messages (instead of crashing) upon unsuitable call arguments. 
  - I am no longer convinced that the title word in citation keys and PDF filenames is useful.
    (even once it works better and ignores stopwords)
    I suggest to leave it out by default and only add it if `--longname` is given.
- tech debt reductions:
- defects:
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
