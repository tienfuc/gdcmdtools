#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "gdcmdtools",
    version = "0.2",
    packages = find_packages(),
    scripts = ['gdput.py','gdget.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['requests>=1.2.3','google_api_python_client>=1.1'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "ctf",
    url = "https://github.com/timchen86/gdcmdtools",
    author_email = "tim.chen.86@gmail.com",
    description = "Google drive command-line tools",
    license = "BSD",
    dependency_links = ['https://github.com/timchen86/gdcmdtools/tarball/master#egg=gdcmdtools-0.0.1']
)
