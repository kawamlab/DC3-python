# Author: Ryosuke1218, being24 <34680324+being24@users.noreply.github.com>
# Copyright (c) 2023- Ryosuke1218, being24
# Licence: MIT

from setuptools import setup

DESCRIPTION = "dc3client: Client of Digital Curing3."
NAME = "dc3client"
AUTHOR = "Ryosuke1218"
AUTHOR_EMAIL = "34680324+being24@users.noreply.github.com"
URL = "https://github.com/kawamlab/DC3-python"
LICENSE = "MIT"
DOWNLOAD_URL = URL
VERSION = "0.0.9"
INSTALL_REQUIRES = ["numpy >= 1.25.1 , < 2.0.0"]
PACKAGES = ["dc3client"]
KEYWORDS = "digital-curing3 dc3client"
CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
]
with open("README.md", "r", encoding="utf-8") as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    download_url=URL,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES,
)
