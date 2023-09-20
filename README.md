# dc3client

Wrapper for developing digitalcuring3 clients in python

If issues are found, please report them via GitHub issues.

## Installation

Python 3.10 or higher is required
```bash
pip install dc3client
```

## Usage

see [sample.py](https://github.com/kawamlab/DC3-python/blob/master/sample.py)

## Create document

from [here](https://zero-cheese.com/12248/)
```sh
sphinx-quickstart docs # init
```
```sh
sphinx-apidoc -f -o ./docs/source/ ./
sphinx-build  ./docs/source/ ./docs/
```