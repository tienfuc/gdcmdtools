#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "gdcmdtools",
    version = "0.1",
    packages = find_packages(),
    # scripts = ['say_hello.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['requests>=1.2.3'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "ctf",
    author_email = "tim.chen.86@gmail.com",
    description = "Google drive command-line tools",
    license = "BSD",
    url = "https://github.com/timchen86/gdcmdtools",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
