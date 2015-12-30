#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.about import GDAbout

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import help_permission_text

import csv
import pprint

__THIS_APP = 'gdabout'
__THIS_DESCRIPTION = 'Tool to get metadata of file/folder on Google Drive'
__THIS_VERSION = BASE_INFO["version"]

import logging
logger = logging.getLogger(__THIS_APP)


def test():
    assert True

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='%s v%s - %s - %s (%s)' %
        (__THIS_APP,
         __THIS_VERSION,
         __THIS_DESCRIPTION,
         BASE_INFO["app"],
         BASE_INFO["description"]),
        formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument(
        '--no_print_id',
        action='store_true',
        help='set if you like not to print the folder id after folder being created')

    arg_parser.add_argument('--debug',
                            choices=DEBUG_LEVEL,
                            default=DEBUG_LEVEL[-1],
                            help='define the debug level')

    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    about = GDAbout(args)

    try:
        response = about.run()
    except:
        raise

    logger.debug(pprint.pformat(response))

    sys.exit(0)
