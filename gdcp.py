#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.cp import GDCp

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import help_permission_text

import csv
import pprint

__THIS_APP = 'gdcp'
__THIS_DESCRIPTION = 'Tool to copy file/folder on Google Drive'
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
        'id',
        help='The file/folder id or drive link to copy')

    arg_parser.add_argument(
        '-t',
        '--new_title',
        help='the title for the new file')

    now = strftime("%Y-%b-%d %H:%M:%S %Z", localtime())
    arg_parser.add_argument(
        '-d', '--target_description', default='created by %s v%s\ndate: %s' %
        (__THIS_APP, __THIS_VERSION, now), help='specify the description of the folder')

    arg_parser.add_argument(
        '--no_print_id',
        action='store_true',
        help='set if you like not to print the folder id after folder being created')

    arg_parser.add_argument('-f', '--parent_folderId',
                            help='copy the file to folder specified by Id')

    arg_parser.add_argument('--debug',
                            choices=DEBUG_LEVEL,
                            default=DEBUG_LEVEL[-1],
                            help='define the debug level')

    PERMISSION_METAVAR = ('TYPE', 'ROLE', 'VALUE')
    arg_parser.add_argument(
        '-p',
        '--permission',
        metavar=PERMISSION_METAVAR,
        nargs=len(PERMISSION_METAVAR),
        help="set the permission of the created folder, can be:\n" +
        '\n'.join(help_permission_text) +
        '\nvalue: user or group e-mail address,\nor \'me\' to refer to the current authorized user\n' +
        'ex: -p anyone reader me # set the uploaded file public-read')
    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    cp = GDCp(args)

    try:
        is_folder, response = cp.run()
    except:
        raise

    logger.debug(pprint.pformat(response))

    if not args.no_print_id:
        if is_folder:
            print "Total files copied: %d" % response["total"]
        else:
            id = response.get("id",None)
            alternateLink = response.get("alternateLink",None)
            webContentLink = response.get("webContentLink",None)
            exportLinks = response.get('exportLinks',None)
        
            if id:
                print "id: %s" % id

            if alternateLink:
                drive_view_prefix = "https://drive.google.com/drive/folders"
                print "drive view: %s" % alternateLink

            if webContentLink:
                print "download url: %s" % webContentLink

            if exportLinks:
                for format, url in exportLinks.iteritems():
                    print "%s: %s" % (format, url)

    sys.exit(0)
