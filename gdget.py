#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from gdcmdtools.base import BASE_INFO
#https://docs.google.com/document/d/1MNFK2buHdqw/export?format=pdf

from gdcmdtools.get import GDGet

import argparse
from argparse import RawTextHelpFormatter


from pprint import pprint

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__THIS_APP = 'gdget'
__THIS_DESCRIPTION = 'Tool to download file from Google Drive'
__THIS_VERSION = '0.0.1'


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file_id', help='The id for the file you\'re going to download')
    
    arg_parser.add_argument('-f', '--export_format', metavar='FORMAT', required=True, help='specify the format for downloading') 
    arg_parser.add_argument('-s', '--save_as', metavar='NEW_FILE_NAME', help='save the downloaded file as ') 


    args = arg_parser.parse_args()

    print args

    get = GDGet(args.file_id, args.export_format, args.save_as)
    result = get.run()
    pprint(result)
