#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import urllib
import requests
import json
import pprint
import re

import logging
logger = logging.getLogger("gdrm")

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth

class GDRm:
    def __init__(self, args):

        for key, value in vars(args).items():
            setattr(self, key, value)

        auth = GDAuth()

        creds = auth.get_credentials()
        self.auth_user = creds.id_token.get("email",None)
        if creds == None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

        file_id_from_link = re.search("^.*/d/([\w\-]*)|^.*/folders/([\w\-]*)", self.file_id)
        
        if file_id_from_link != None:
            self.file_id = file_id_from_link.group(1) or file_id_from_link.group(2)

        logger.debug(self)

    def run(self):
        try:
            if self.delete:
                response = self.service.files().delete(fileId=self.file_id).execute()
            else:
                response = self.service.files().trash(fileId=self.file_id).execute()
        except Exception, e:
            logger.error(e)
            raise
        else:
           return response
