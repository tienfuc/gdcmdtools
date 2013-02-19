#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from argparse import RawTextHelpFormatter

from gdcmdtools.csv import GDCSV
from gdcmdtools.base import *


'''
base = GDBase()


creds = base.get_credentials(True)
http = base.get_authorized_http(creds)
drive = base.get_service()

print(drive)



csv = GDCSV()

csv.put(drive, "./example.csv")
'''
THIS_APP = 'gdput'

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
            description='%s v%s - %s (%s)' % \
                    (THIS_APP, BASE_VERSION, BASE_APP, BASE_DESCRIPTION),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file', 
            help='The file you\'re going to upload to Google Drive')

    arg_group = arg_parser.add_mutually_exclusive_group()

    arg_group.add_argument('-a', '--auto_type', action='store_true',
            help='(default) the source file type will be determinted automatically')

    arg_group.add_argument('-m', '--mime_type', 
            help='define the source file type by MIME, ex: "text/csv"')
   
    arg_parser.add_argument('-t', '--target_type', choices=["raw", "ss", "ft"],
            help='define the target file type on Google Drive, could be:\r\
            raw: the source file will uploaded without touching\r\
            ss: Spreadsheet, if the source is CSV file\r\
            ft: Fusion Table, if the source is CSV file')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    arg_parser.add_argument('-s', '--secret_file', 
            help='specify the oauth2 secret file(in JSON format)')

    arg_parser.add_argument('-c', '--credential_file', 
            help='specify the oauth2 credential file(in JSON format)')

    arg_parser.add_argument('-r', '--redirect_uri', choices=["oob", "localhost"],
            help='specify the redirect URI for the oauth2 flow, could be:\r\
            oob: is "urn:ietf:wg:oauth:2.0:oob"\r\
            localhost: is "http://localhost"\r')



    args = arg_parser.parse_args()
    logger.debug(args)
