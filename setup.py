#!/usr/bin/env python

from gdcmdtools.base import BASE_INFO
from setuptools import setup, find_packages
setup(
    name = "gdcmdtools",
    version = BASE_INFO["version"],
    packages = find_packages(),
    scripts = ['gdput.py','gdget.py','gdperm.py','gdauth.py', 'gdrm.py', 'gdmkdir.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['requests>=1.2.3','google_api_python_client>=1.1','requests_oauthlib>=0.4.2'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "ctf <tienfu.c@gmail.com>",
    url = "https://github.com/tienfuc/gdcmdtools",
    author_email = "tienfu.c@gmail.com",
    description = "Google drive command-line tools",
    license = "BSD",
    dependency_links = ['https://github.com/tienfuc/gdcmdtools/tarball/master']
)
