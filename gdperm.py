#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gdcmdtools.perm import permission_resource_properties
import argparse
from argparse import RawTextHelpFormatter


from gdcmdtools.base import BASE_INFO

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__THIS_APP = 'gdperm'
__THIS_DESCRIPTION = 'Tool to change file\'s permission on Google Drive'
__THIS_VERSION = '0.0.1'


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument('file_id', help='The id of file you\'re going to change permission') 
 
    mutex_group = arg_parser.add_mutually_exclusive_group(required=False)

    mutex_group.add_argument('--list', action='store_true', help='list the permission resource of the file') 
    mutex_group.add_argument('--get', metavar='RESOURCE_ID', help='get the permission resource of the file') 

    mutex_group.add_argument('--insert', nargs=3, metavar=('TYPE', 'ROLE', 'VALUE'), help='insert the permission to the file')

    mutex_group.add_argument('--delete', action='store_true', help='delete the permission of the file')

    args = arg_parser.parse_args()
 



    # xor insert delete 
