#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from time import localtime, strftime

import argparse
from argparse import RawTextHelpFormatter
import mimetypes

from gdcmdtools.put import GDPut 
from gdcmdtools.put import DICT_OF_CONVERTIBLE_FILE_TYPE
from gdcmdtools.put import DICT_OF_REDIRECT_URI

from gdcmdtools.base import BASE_INFO

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__THIS_APP = 'gdput'
__THIS_VERSION = '0.0.1'

def get_mime_type(filename, source_type):
    # check source_type
    source_type = source_type.lower()
    mimetypes.init()
    if source_type == "auto":
        # let's guess
        source_mime_type = mimetypes.guess_type(filename, False)[0]
    else:
        # user define the mime type
        suffix = mimetypes.guess_all_extensions(source_type, False)
        if len(suffix) < 1:
            return (False, None)

        source_mime_type = source_type

    return (True, source_mime_type)
    

class verify_location_column(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        if getattr(args, 'ft_location_column') is None:
            parser.error('--ft_location_column must be used with --ft_latlng_column')
        setattr(args, self.dest, values)

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('source_file', 
            help='The file you\'re going to upload to Google Drive')

    # FIXME: mime_type = auto to replace --auto_type
    arg_parser.add_argument('-s', '--source_type', default="auto",
            help='define the source file type by MIME type, ex: "text/csv", or \"auto\" to determine the file type by file name')
   
    arg_parser.add_argument('-l', '--target_title', default=None, 
            help='specify the title of the target file')

    now = strftime("%Y-%b-%d %H:%M:%S %Z", localtime()) 
    arg_parser.add_argument('-d', '--target_description', default='uploaded by %s v%s\ndate: %s' % (__THIS_APP, __THIS_VERSION, now),
            help='specify the description of the target file')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    d_file_types = DICT_OF_CONVERTIBLE_FILE_TYPE
    choices_target_type = list(d_file_types.keys())
    l_file_types_wo_raw = list(d_file_types.keys())
    l_file_types_wo_raw.remove("raw") 

    # FIXME: readible-----
    # make the help text from DICT_OF_CONVERTIBLE_FILE_TYPE
    list_help_target_type = \
            [ (k+": "+
                d_file_types[k][0]+ " (for ."+
                ', .'.join(d_file_types[k][1])+')') \
                        for k in l_file_types_wo_raw ]
    
    help_target_type = '\n'.join(list_help_target_type)

    arg_parser.add_argument('-t', '--target_type', default="raw",
            choices=choices_target_type,
            help='define the target file type on Google Drive, could be:\n'+
            "raw: (default) the source file will uploaded without touching\n"+
            help_target_type)


    group = arg_parser.add_argument_group('fusion table geocoding')

    group.add_argument('--ft_location_column', 
            help=
            'specify the location column header for the fusion table '+
            '(if target_type is ft)')

    group.add_argument('--ft_latlng_column', 
            action=verify_location_column,
            help=
            'specify the column header for latitude and longitude for the fusion table'+
			'(if target_type is ft and --ft_location_column is used)'+
            ', the column will be created if not present' )

    choices_redirect_uri = list(DICT_OF_REDIRECT_URI.keys())
    list_help_redirect_uri = \
            [ (k+": "+DICT_OF_REDIRECT_URI[k]) for k in DICT_OF_REDIRECT_URI] 
    help_redirect_uri = '\n'.join(list_help_redirect_uri)

    arg_parser.add_argument('-r', '--redirect_uri', choices=choices_redirect_uri,
            default="oob",
            help=
            'specify the redirect URI for the oauth2 flow, could be:\n%s' % 
            help_redirect_uri)

    args = arg_parser.parse_args()

    logger.debug(args)

    # check source file if exists
    try:
        with open(args.source_file) as f: pass
    except IOError as e:
        logger.error(e)
        sys.exit(1)

    # check source_type
    (r_mime_type, mime_type) = get_mime_type(args.source_file, args.source_type)

    if not r_mime_type:
        logger.error("Invalid MIME type: %s" % args.source_type)
        sys.exit(1)
    else:
        logger.debug("mime_type=%s" % mime_type)

    # check direct uri
    if args.redirect_uri == "oob":
        if_oob = True
    elif args.redirect_uri == "local":
        if_oob = False
    else:
        logger.error("failed to determine redirect_uri")
        sys.exit(1)

    # check title
    target_title = args.target_title
    if (target_title == None) or (target_title == ''):
        target_title = os.path.basename(args.source_file)
    logger.debug("target_title=%s", target_title)

    # let's put
    puter = GDPut(
            args.source_file, 
            mime_type, 
            args.target_type,
            args.folder_id,
            target_title,
            args.target_description,
            if_oob,
			args.ft_location_column,
			args.ft_latlng_column)

    try:
        target_link = puter.run()
    except:
        sys.exit(1)

    logger.info("The uploaded file is located at: %s" % 
            target_link)
