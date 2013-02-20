#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.csv import GDCSV
from gdcmdtools.base import *

THIS_APP = 'gdput'

__CHOICES_TARGET_TYPE = {
    "raw":"(default) the source file will uploaded without touching",
    "ss":"Spreadsheet (for .xls, .xlsx, .ods, .csv, .tsv, .txt, .tab)",
    "ft":"Fusion Table (for .csv)",
    "pt":"Presentation (for .ppt, .pps, .pptx)",
    "dr":"Drawing (for .wmf)",
    "ocr":"OCR (for .jpg, .gif, .png, .pdf)",
    "doc":"Document (for .doc, .docx, .html, .htm, .txt, .rtf)"
    }

__CHOICES_REDIRECT_URI = {
    "oob":"(default) means \"urn:ietf:wg:oauth:2.0:oob\"",
    "local":"means \"http://localhost\""
    }

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
            description='%s v%s - %s (%s)' % \
                    (THIS_APP, BASE_VERSION, BASE_APP, BASE_DESCRIPTION),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file', 
            help='The file you\'re going to upload to Google Drive')

    arg_group = arg_parser.add_mutually_exclusive_group()

    arg_group.add_argument('-a', '--auto_type', action='store_true', default=True, 
            help='(default) the type of the source file will be determinted automatically')

    arg_group.add_argument('-m', '--mime_type', 
            help='define the source file type by MIME, ex: "text/csv"')
   
    arg_parser.add_argument('-l', '--new_title', 
            help='specify the title of the target file')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    choices_target_type = list(__CHOICES_TARGET_TYPE.keys())
    list_help_target_type = [ (k+": "+__CHOICES_TARGET_TYPE[k]) for k in __CHOICES_TARGET_TYPE ] 
    help_target_type = '\n'.join(list_help_target_type)
    
    arg_parser.add_argument('-t', '--target_type', default="raw",
            choices=choices_target_type,
            help='define the target file type on Google Drive, could be:\n%s' % help_target_type)

    arg_parser.add_argument('--ft_location_column', 
            help=
            'specify the location column header for the fusion table (if target_type is ft)')

    arg_parser.add_argument('-s', '--secret_file', 
            help='specify the oauth2 secret file')

    arg_parser.add_argument('-c', '--credential_file', 
            help='specify the oauth2 credential file')

    choices_redirect_uri = list(__CHOICES_REDIRECT_URI.keys())
    list_help_redirect_uri = [ (k+": "+__CHOICES_REDIRECT_URI[k]) for k in __CHOICES_REDIRECT_URI] 
    help_redirect_uri = '\n'.join(list_help_redirect_uri)
    arg_parser.add_argument('-r', '--redirect_uri', choices=choices_redirect_uri,
            default="oob",
            help='specify the redirect URI for the oauth2 flow, could be:\n%s' % help_redirect_uri)

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


