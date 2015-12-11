#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import urllib
import requests
import json
import pprint

import logging
logger = logging.getLogger("gdmkdir")

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth

class GDMkdir:
    def __init__(self, args):

        logger.debug(vars(args))

        for key, value in vars(args).items():
            setattr(self, key, value)

        self.mime_type = "application/vnd.google-apps.folder"
        auth = GDAuth()

        creds = auth.get_credentials()
        self.auth_user = creds.id_token.get("email",None)
        if creds == None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

        logger.debug(self)

    def run(self):
        if self.parent_folderId == None:
            parents = []
        else:
            parents = [{
                "kind":"drive#fileLink",
                "id":self.parent_folderId}]

        body = {
                'title':self.folder_name,
                'description':self.target_description,
                'mimeType':self.mime_type,
                'parents':parents}

        try:
            response_insert = self.service.files().insert(body=body).execute()
        except Exception, e:
            logger.error(e)
            raise
        else:
            if (self.permission != None) and response_insert.get('id') != None:
                try:
                    param = {
                            'name':'insert',
                            'param':self.permission}

                    perm = GDPerm(response_insert['id'], param)
                    response_perm = perm.run()
                except Exception, e:
                    logger.error(e)
                    raise

        return response_insert
