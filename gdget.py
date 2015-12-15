#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL 

from gdcmdtools.get import GDGet
from gdcmdtools.get import export_format

import argparse
from argparse import RawTextHelpFormatter


from pprint import pprint

import logging
logger = logging.getLogger()

__THIS_APP = 'gdget'
__THIS_DESCRIPTION = 'Tool to download file from Google Drive'
__THIS_VERSION = BASE_INFO["version"]

# u'exportLinks': {u'application/vnd.google-apps.script+json': u'https://script.google.com/feeds/download/export?id=1u3Im-CCiTDpaKpJ6JqMgDRxKoi2TdCdaHAg65jcseyL-x0NSL7dRZs7z&format=json'}

"""
u'exportLinks': {u'application/pdf': u'https://docs.google.com/feeds/download/presentations/Export?id=1lxwOegts6hKssHtjH6
Dj0WPbwlF71KhFGLSnCtruraY&exportFormat=pdf',
                  u'application/vnd.openxmlformats-officedocument.presentationml.presentation': u'https://docs.google.com/
                  feeds/download/presentations/Export?id=1lxwOegts6hKssHtjH6Dj0WPbwlF71KhFGLSnCtruraY&exportFormat=pptx',
                                    u'text/plain': u'https://docs.google.com/feeds/download/presentations/Export?id=1lxwOegts6hKssHtjH6Dj0WP
                                    bwlF71KhFGLSnCtruraY&exportFormat=txt'}
"""

def test():
    assert True

if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file_id', help='The file id or drive link for the file you\'re going to download')
    
    help_export_format = "\n".join([ re.search(".*google-apps\.(.*)", k ).group(1)+": "+", ".join(export_format[k]) for k in export_format.iterkeys() ])

    arg_parser.add_argument('-f', '--export_format', metavar='FORMAT', default='raw', required=False, help='specify the export format for downloading,\ngoogle_format: export_format\n%s' % help_export_format) 
    arg_parser.add_argument('-s', '--save_as', metavar='NEW_FILE_NAME', help='save the downloaded file as ') 

    arg_parser.add_argument('--debug', choices=DEBUG_LEVEL, default=DEBUG_LEVEL[-1],
            help='define the debug level')


    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))
    logger.debug(args)

    get = GDGet(args.file_id, args.export_format, args.save_as)
    result = get.run()
    

    sys.exit(0)
