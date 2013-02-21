#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import argparse
from argparse import RawTextHelpFormatter
import mimetypes


from gdcmdtools.csv import GDCSV
from gdcmdtools.base import *

logger = logging.getLogger( __name__ )
logger.setLevel(logging.DEBUG)

THIS_APP = 'gdput'
THIS_VERSION = '0.0.1'

__DICT_OF_CONVERTIBLE_FILE_TYPE = { \
        'ss':[
            "Spreadsheet",
            ['xls', 'xlsx', 'ods', 'csv', 'tsv', 'tab']],
        'ft':[
            "Fusion Table",
            ['csv']],
        'pt':[
            "Presentation",
            ['ppt', 'pps', 'pptx']],
        'dr':[
            "Drawing",
            ['wmf']],
        'ocr':[
            "OCR",
            ['jpg', 'git', 'png', 'pdf']],
        'doc':[
            "Document",
            ['doc', 'docx', 'html', 'htm', 'txt', 'rtf']]
        }

__DICT_OF_REDIRECT_URI = {
    "oob":"(default) means \"urn:ietf:wg:oauth:2.0:oob\"",
    "local":"means \"http://localhost\""
    }


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s (%s)' % 
            (THIS_APP, THIS_VERSION, BASE_APP, BASE_DESCRIPTION),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('source_file', 
            help='The file you\'re going to upload to Google Drive')

    # FIXME: mime_type = auto to replace --auto_type
    arg_parser.add_argument('-s', '--source_type', default="auto",
            help='define the source file type by MIME type, ex: "text/csv", or \"auto\" to determine the file type by file name')
   
    arg_parser.add_argument('-l', '--new_title', 
            help='specify the title of the target file')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    choices_target_type = list(__DICT_OF_CONVERTIBLE_FILE_TYPE.keys())

    # FIXME: readible-----
    # make the help text from __DICT_OF_CONVERTIBLE_FILE_TYPE
    list_help_target_type = \
            [ (k+": "+
                __DICT_OF_CONVERTIBLE_FILE_TYPE[k][0]+ " (for ."+
                ', .'.join(__DICT_OF_CONVERTIBLE_FILE_TYPE[k][1])+')') \
                        for k in __DICT_OF_CONVERTIBLE_FILE_TYPE]

    help_target_type = '\n'.join(list_help_target_type)
    
    arg_parser.add_argument('-t', '--target_type', default="raw",
            choices=choices_target_type,
            help='define the target file type on Google Drive, could be:\n'+
            "raw: (default) the source file will uploaded without touching\n"+
            help_target_type)

    arg_parser.add_argument('--ft_location_column', 
            help=
            'specify the location column header for the fusion table '+
            '(if target_type is ft)')

    """
    arg_parser.add_argument('-s', '--secret_file', 
            help='specify the oauth2 secret file')

    arg_parser.add_argument('-c', '--credential_file', 
            help='specify the oauth2 credential file')

    """

    choices_redirect_uri = list(__DICT_OF_REDIRECT_URI.keys())
    list_help_redirect_uri = \
            [ (k+": "+__DICT_OF_REDIRECT_URI[k]) for k in __DICT_OF_REDIRECT_URI] 
    help_redirect_uri = '\n'.join(list_help_redirect_uri)

    arg_parser.add_argument('-r', '--redirect_uri', choices=choices_redirect_uri,
            default="oob",
            help=
            'specify the redirect URI for the oauth2 flow, could be:\n%s' % 
            help_redirect_uri)


    args = arg_parser.parse_args()

    logger.debug(args)

    # check source file
    try:
        with open(args.source_file) as source_file: pass
    except IOError as e:
        logger.error(e)
        sys.exit(1)

    # check source_type
    source_type = args.source_type.lower()
    mimetypes.init()
    if source_type == "auto":
        # let's guess
        source_mime_type = mimetypes.guess_type(args.source_file, False)[0]
    else:
        # user define the mime type
        #source_mime_type = source_type
        source_mime_type = mimetypes.guess_all_extensions(source_type,False)
        if len(source_mime_type) < 1:
            logger.error("MIME type invalid: %s" % source_type)
            sys.exit(1)

    logger.debug("source_mime_type=%s" % source_mime_type)


    '''
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

    '''

    #csv = GDCSV()


