#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gdcmdtools.perm import GDPerm
from gdcmdtools.perm import help_permission_text
import argparse
from argparse import RawTextHelpFormatter
from gdcmdtools.base import BASE_INFO
from gdcmdtools.base import DEBUG_LEVEL

from pprint import pprint

import sys

import logging
logger = logging.getLogger()

__THIS_APP = 'gdperm'
__THIS_DESCRIPTION = 'Tool to change file\'s permission on Google Drive'
__THIS_VERSION = BASE_INFO["version"]


def test():
    file_id = "https://drive.google.com/open?id=0B60IjoJ-xHK6YU1wZ2hsQVQ0SzA"
    permission_id = "02914492818163807046i"

    action1 = {
        'name': 'update',
        'param': [
            permission_id,
            'user',
            'reader',
            'test@gdcmdtools.com']}
    action2 = {
        'name': 'update',
        'param': [
            permission_id,
            'user',
            'writer',
            'test@gdcmdtools.com']}

    for action in [action1, action2]:
        perm = GDPerm(file_id, action)
        result = perm.run()
        pprint(result)

        assert result[u"role"] == action["param"][2]


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(
        description='%s v%s - %s - %s (%s)' %
        (__THIS_APP,
         __THIS_VERSION,
         __THIS_DESCRIPTION,
         BASE_INFO["app"],
         BASE_INFO["description"]),
        formatter_class=RawTextHelpFormatter)

    arg_parser.add_argument(
        'file_id',
        help='The id for the file you\'re going to change permission')

    mutex_group = arg_parser.add_mutually_exclusive_group(required=False)

    mutex_group.add_argument(
        '--list',
        action='store_true',
        help='list the permission resource of the file')
    mutex_group.add_argument(
        '--get',
        metavar='PERMISSION_ID',
        help='get the permission resource by id')

    PERMISSION_METAVAR = ('TYPE', 'ROLE', 'VALUE')
    mutex_group.add_argument(
        '--insert',
        metavar=PERMISSION_METAVAR,
        nargs=len(PERMISSION_METAVAR),
        help="set the permission of the created folder, can be:\n" +
        '\n'.join(help_permission_text) +
        '\nvalue: user or group e-mail address,\nor \'me\' to refer to the current authorized user\n' +
        'ex: -p anyone reader me # set the uploaded file public-read')

    UPDATE_PERMISSION_METAVAR = ("PERMISSION_ID",) + PERMISSION_METAVAR
    mutex_group.add_argument(
        '--update',
        metavar=UPDATE_PERMISSION_METAVAR,
        nargs=len(UPDATE_PERMISSION_METAVAR),
        help="update the permission, refer to the help of --insert")

    mutex_group.add_argument(
        '--delete',
        metavar='PERMISSION_ID',
        help='delete the permission of the file by id')

    mutex_group.add_argument(
        '--get_by_user',
        metavar='USER_EMAIL',
        help='get the permission associated with user')

    arg_parser.add_argument('--debug',
                            choices=DEBUG_LEVEL,
                            default=DEBUG_LEVEL[-1],
                            help='define the debug level')

    args = arg_parser.parse_args()

    # set debug devel
    logger.setLevel(getattr(logging, args.debug.upper()))

    action = {}
    valid_actions = [
        "list",
        "get",
        "insert",
        "update",
        "delete",
        "get_by_user"]
    for a in valid_actions:
        action[a] = args.__dict__[a]

    # check which action is given by argument
    for act in action:
        if action[act] != mutex_group.get_default(act):
            pass_action = {"name": act, "param": action[act]}
            logger.debug("pass_action=%s" % pass_action)
            perm = GDPerm(args.file_id, pass_action)
            result = perm.run()
            pprint(result)

            if result is None:
                sys.exit(1)
            else:
                sys.exit(0)

    logger.error('unexpected error')
    sys.exit(1)
