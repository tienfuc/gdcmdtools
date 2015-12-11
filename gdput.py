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
from gdcmdtools.auth import DICT_OF_REDIRECT_URI

from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL
from gdcmdtools.perm import permission_resource_properties

import csv


__THIS_APP = 'gdput'
__THIS_DESCRIPTION = 'Tool to upload file to Google Drive'
__THIS_VERSION = BASE_INFO["version"]

import logging
logger = logging.getLogger(__THIS_APP)

#formatter = logging.Formatter('%(levelname)s:%(name)s:%(lineno)d:%(message)s')

#handler = logging.StreamHandler()
#handler.setFormatter(formatter)
#logger.addHandler(handler)

def test():
    assert True 


def check_column_type(source_file, csv_column_define):
    with open(source_file, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file)
        csv_lines = len(csv_reader.next())
        column_numbers = len(csv_column_define)
        
        if csv_lines == column_numbers:
            return True
        else:
            return False   


def get_mime_type(filename, source_type):
    # check source_type
    source_type = source_type.lower()
    mimetypes.init()
    if source_type == "auto":
        # let's guess
        source_mime_type = mimetypes.guess_type(filename, False)[0]
        if source_mime_type == None:
            source_mime_type = "application/octet-stream"
    else:
        # user define the mime type
        suffix = mimetypes.guess_all_extensions(source_type, False)
        if len(suffix) < 1:
            return (False, None)

        source_mime_type = source_type

    return (True, source_mime_type)
    

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('source_file', 
            help='The file you\'re going to upload to Google Drive')

    # FIXME: mime_type = auto to replace --auto_type
    arg_parser.add_argument('-s', '--source_type', default="auto",
            help='define the source file type by MIME type,\nex: "text/csv", or \"auto\" to determine the file type by file name')
   
    arg_parser.add_argument('-r', '--replace_id', default=None, 
            help='replace the file with specifying the file id')

    arg_parser.add_argument('-l', '--target_title', default=None, 
            help='specify the title of the target file')

    now = strftime("%Y-%b-%d %H:%M:%S %Z", localtime()) 
    arg_parser.add_argument('-d', '--target_description', default='uploaded by %s v%s\ndate: %s' % (__THIS_APP, __THIS_VERSION, now),
            help='specify the description of the target file')

    arg_parser.add_argument('--no_print_id', action='store_true', 
            help='set if you like not to print the file id after file being uploaded')

    arg_parser.add_argument('-f', '--folder_id', 
            help='the target folder ID on the Google drive')

    arg_parser.add_argument('--debug', choices=DEBUG_LEVEL, default=DEBUG_LEVEL[-1],
            help='define the debug level')

    d_file_types = DICT_OF_CONVERTIBLE_FILE_TYPE
    choices_target_type = list(d_file_types.keys())
    l_file_types_wo_raw = list(d_file_types.keys())
    l_file_types_wo_raw.remove("raw") 

    # FIXME: it's hard to read..
    # make the help text from DICT_OF_CONVERTIBLE_FILE_TYPE
    list_help_target_type = \
            [ (k+": "+
                d_file_types[k][0]+ " (for ."+
                ', .'.join(d_file_types[k][1])+')') \
                        for k in l_file_types_wo_raw ]
    
    help_target_type = '\n'.join(list_help_target_type)

    help_permission_text = [(j+": "+', '.join(permission_resource_properties[j])) for j in permission_resource_properties.keys()]


    PERMISSION_METAVAR = ('TYPE', 'ROLE', 'VALUE')
    arg_parser.add_argument('-p', '--permission',
            metavar=PERMISSION_METAVAR,
            nargs=len(PERMISSION_METAVAR),
            help = "set the permission of the uploaded file, can be:\n" + '\n'.join(help_permission_text) + \
                    '\nvalue: user or group e-mail address,\nor \'me\' to refer to the current authorized user\n'+
                    'ex: -p anyone reader me # set the uploaded file public-read')

    arg_parser.add_argument('-t', '--target_type', default="raw",
            choices=choices_target_type,
            help='define the target file type on Google Drive, can be:\n'+
            "raw: (default) the source file will uploaded without touching\n"+
            help_target_type)

    ft_group = arg_parser.add_argument_group('fusion table support (--target_type ft)')

    ft_group.add_argument('--ft_latlng_column', 
            help=
            'specify the column header for latitude and longitude for the fusion table,\n'+
            'the column will be created automatically' )

    ft_group.add_argument('--ft_location_column', 
            help=
            'specify the location column header for the fusion table')

    ft_group.add_argument('--csv_column_define',
            metavar='define1_define2_defineN...',
            help = 'define the columns type for each column of the csv file,\ncan be "string", "number", "datetime", or "location".\nex: has 4 columns in the csv file: "name", "age", "birthday", "address".\nyou can set --csv_column_define string_number_datetime_location')

    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    logger.debug(args)

    ## post-processing of argument parsing
    # 
    if (getattr(args, 'ft_latlng_column', None) == None) != (getattr(args, 'ft_location_column', None) == None):
        arg_parser.error("must supply --ft_location_column with --ft_latlng_column")

    # check source file if exists
    try:
        with open(args.source_file) as f: pass
    except:
        raise
        sys.exit(1)

    # check column type
    if args.csv_column_define != None: 
        # FIXME: if the column contain '_' character?
        csv_column_define = args.csv_column_define.upper().split('_')
        if check_column_type(args.source_file, csv_column_define) != True: 
            arg_parser.error('Check option --csv_column_define')
    else:
        csv_column_define = None
            


    # check source_type
    (r_mime_type, mime_type) = get_mime_type(args.source_file, args.source_type)

    if not r_mime_type:
        logger.error("Invalid MIME type: %s" % args.source_type)
        sys.exit(1)
    else:
        logger.debug("mime_type=%s" % mime_type)

    # check title
    target_title = args.target_title
    if (target_title == None) or (target_title == ''):
        target_title = os.path.basename(args.source_file)
    logger.debug("target_title=%s", target_title)

    # let's put
    puter = GDPut(
            source_file = args.source_file,
            replace_id = args.replace_id,
            mime_type = mime_type,
            target_type = args.target_type,
            folder_id = args.folder_id,
            title = target_title,
            description = args.target_description,
            ft_location_column = args.ft_location_column,
            ft_latlng_column = args.ft_latlng_column,
            permission = args.permission,
            csv_column_define = csv_column_define)

    try:
        response = puter.run()
    except:
        raise
        sys.exit(1)

    logger.debug(response)
    
    if not args.no_print_id:
        print "id: %s" % response['id']
        print "drive url: %s" % response[u'alternateLink']

        if response.get(u'webContentLink'):
            print "download url: %s" % response.get('webContentLink')
        exports = response.get('exportLinks')
        if exports:
            for format, url in exports.iteritems():
                print "%s: %s" % (format, url)

    sys.exit(0)
