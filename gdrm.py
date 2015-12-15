#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.rm import GDRm

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import help_permission_text 

import csv
import pprint

__THIS_APP = 'gdrm'
__THIS_DESCRIPTION = 'Tool to remove file or folder on Google Drive'
__THIS_VERSION = BASE_INFO["version"]

import logging
logger = logging.getLogger(__THIS_APP)

def test():
    assert True 
   
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('-d', '--delete', action='store_true', help='Permanently deletes the file instead of trashing it')

    arg_parser.add_argument('file_id', help='The file id or drive link for the file you\'re going to remove')

    arg_parser.add_argument('--debug', choices=DEBUG_LEVEL, default=DEBUG_LEVEL[-1],
            help='define the debug level')

    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    rm = GDRm(args)

    try:
        response = rm.run()
    except:
        raise

    logger.debug(pprint.pformat(response))

    sys.exit(0)
