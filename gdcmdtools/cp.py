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
logger = logging.getLogger("gdcp")

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth


class GDCp:

    def __init__(self, args):

        for key, value in vars(args).items():
            setattr(self, key, value)

        auth = GDAuth()

        creds = auth.get_credentials()
        self.auth_user = creds.id_token.get("email", None)
        if creds is None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

        self.id = base.get_id_from_url(self.id)

    @property
    def is_folder(self):
        # u'mimeType': u'application/vnd.google-apps.folder'
        # u'mimeType': u'application/vnd.google-apps.document'
        try:
            response = self.service.files().get(fileId=self.id).execute()
        except Exception as e:
            logger.error(e)
            raise
        else:
            raw = response['mimeType']
            folder_mime = 'application/vnd.google-apps.folder'

            return (raw == folder_mime)
    
    def copy_dir(self):
        return None

    def run(self):

        if self.parent_folderId is None:
            parents = []
        else:
            parents = [{
                "kind": "drive#fileLink",
                "id": self.parent_folderId}]

        body = {
            'title': self.new_title,
            'description': self.target_description,
            'parents': parents}

        logger.debug("is_folder: %s", self.is_folder)

        try:
            if self.is_folder:
                response = self.copy_dir()
            else:
                response = self.service.files().copy(fileId=self.id, body=body).execute()
        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
