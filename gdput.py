#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.csv import GDCSV
from gdcmdtools.base import *


THIS_APP = 'gdput'

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
            description='%s v%s - %s (%s)' % \
                    (THIS_APP, BASE_VERSION, BASE_APP, BASE_DESCRIPTION),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file', 
            help='The file you\'re going to upload to Google Drive')

    arg_group = arg_parser.add_mutually_exclusive_group()

    arg_group.add_argument('-a', '--auto_type', action='store_true', default=True, 
            help='(default) the source file type will be determinted automatically')

    arg_group.add_argument('-m', '--mime_type', 
            help='define the source file type by MIME, ex: "text/csv"')
   
    arg_parser.add_argument('-l', '--new_title', 
            help='specify the title of the target file')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    arg_parser.add_argument('-t', '--target_type', choices=["raw", "ss", "ft"],
            help='define the target file type on Google Drive, could be:\r\
            raw: (default) the source file will uploaded without touching\r\
            ss: Spreadsheet (if source is CSV)\r\
            ft: Fusion Table (if source is CSV)')

    arg_parser.add_argument('--ft_location_column', 
            help=
            'specify the location column header for the fusion table\r\
            (if target_type is ft)')

    arg_parser.add_argument('-s', '--secret_file', 
            help='specify the oauth2 secret file(in JSON format)')

    arg_parser.add_argument('-c', '--credential_file', 
            help='specify the oauth2 credential file(in JSON format)')

    arg_parser.add_argument('-r', '--redirect_uri', choices=["oob", "local"],
            default="oob",
            help='specify the redirect URI for the oauth2 flow, could be:\r\
            oob: is "urn:ietf:wg:oauth:2.0:oob"\r\
            local: is "http://localhost"\r')

    args = arg_parser.parse_args()
    logger.debug(args)

    
    base = GDBase()


    if args.redirect_uri == "oob":
        if_oob = True
    elif args.redirect_uri == "local":
        if_oob = False
    else:
        logger.error("failed to determine redirect_uri")
        sys.exit(1)


    logger.debug("if_oob=%s" % if_oob)

    creds = base.get_credentials(if_oob)
    http = base.get_authorized_http(creds)


    root = base.get_root()
    print(root)
    #print(drive)



    #csv = GDCSV()


