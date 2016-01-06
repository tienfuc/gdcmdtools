#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.find import GDFind

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import help_permission_text

from collections import OrderedDict as OD
import json


import csv
import pprint

__THIS_APP = 'gdfind'
__THIS_DESCRIPTION = 'Tool to walk through folder on Google Drive'
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

    arg_parser.add_argument('folder_id',
                            help='Specify the folder id to walk through')

    arg_parser.add_argument('--debug',
                            choices=DEBUG_LEVEL,
                            default=DEBUG_LEVEL[-1],
                            help='define the debug level')
    arg_parser.add_argument(
        '-c', '--copy_mode', 
        action='store_true',
        help='set if you like to copy the folder')

    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    find = GDFind(args)

    try:
        response = find.run()
    except:
        raise

    try:
        from asciitree import LeftAligned
    except:
        print(json.dumps(response, indent=4))
    else:
        tree = LeftAligned()
        print tree(response)

    sys.exit(0)
