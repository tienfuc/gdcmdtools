#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.mkdir import GDMkdir

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import help_permission_text 

import csv
import pprint

__THIS_APP = 'gdmkdir'
__THIS_DESCRIPTION = 'Tool to create folder on Google Drive'
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

    arg_parser.add_argument('folder_name', 
            help='Specify the folder name to be created')

    now = strftime("%Y-%b-%d %H:%M:%S %Z", localtime()) 
    arg_parser.add_argument('-d', '--target_description', default='created by %s v%s\ndate: %s' % (__THIS_APP, __THIS_VERSION, now),
            help='specify the description of the folder')

    arg_parser.add_argument('--no_print_id', action='store_true', 
            help='set if you like not to print the folder id after folder being created')

    arg_parser.add_argument('-f', '--parent_folderId', 
            help='create the new folder under the parent folder specified by Id')

    arg_parser.add_argument('--debug', choices=DEBUG_LEVEL, default=DEBUG_LEVEL[-1],
            help='define the debug level')

    PERMISSION_METAVAR = ('TYPE', 'ROLE', 'VALUE')
    arg_parser.add_argument('-p', '--permission',
            metavar=PERMISSION_METAVAR,
            nargs=len(PERMISSION_METAVAR),
            help = "set the permission of the created folder, can be:\n" + '\n'.join(help_permission_text) + \
                    '\nvalue: user or group e-mail address,\nor \'me\' to refer to the current authorized user\n'+
                    'ex: -p anyone reader me # set the uploaded file public-read')
    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    mkdir = GDMkdir(args)

    try:
        response = mkdir.run()
    except:
        raise

    logger.debug(pprint.pformat(response))

    if not args.no_print_id:
        print "id: %s" % response['id']
        driver_view_prefix = "https://drive.google.com/drive/folders"
        print "driver view: %s/%s" % (driver_view_prefix, response[u'id'])
        print "folder view: %s" % response[u'alternateLink']

    sys.exit(0)
