#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from gdcmdtools.base import BASE_INFO

from gdcmdtools.auth import GDAuth

import argparse
from argparse import RawTextHelpFormatter


from gdcmdtools.auth import DICT_OF_REDIRECT_URI

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__THIS_APP = 'gdauth'
__THIS_DESCRIPTION = 'Google Drive OAuth2 authentication tool'
__THIS_VERSION = '0.0.1'



if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser( \
            description='%s v%s - %s - %s (%s)' % 
            (__THIS_APP, __THIS_VERSION, __THIS_DESCRIPTION, BASE_INFO["app"], BASE_INFO["description"]),
            formatter_class=RawTextHelpFormatter)

    default_secrets_file = os.path.expanduser('~/.%s.secrets' % BASE_INFO["app"])
    arg_parser.add_argument('secret_file', default=default_secrets_file, help='the secret file in JSON format, %s will be overwritten' % default_secrets_file)

    choices_redirect_uri = list(DICT_OF_REDIRECT_URI.keys())
    list_help_redirect_uri = \
            [ (k+": "+DICT_OF_REDIRECT_URI[k]) for k in DICT_OF_REDIRECT_URI] 
    help_redirect_uri = '\n'.join(list_help_redirect_uri)

    arg_parser.add_argument('-r', '--redirect_uri', choices=choices_redirect_uri,
            default="oob",
            help=
            'specify the redirect URI for the oauth2 flow, can be:\n%s' % 
            help_redirect_uri)


    args = arg_parser.parse_args()
    logger.debug(args)
    

    if args.redirect_uri == 'oob':
        if_oob = True
    else:
        if_oob = False

    auth = GDAuth(args.secret_file, if_oob)

    result = auth.run()

    if result == None:
        logger.error("Failed to pass OAuth2 authentication")
        sys.exit(1)
    else:
        logger.info("The OAuth2 authentication has completed")
        sys.exit(0)
