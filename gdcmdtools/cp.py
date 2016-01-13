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
logger.setLevel(logging.DEBUG)

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth
from gdcmdtools.mkdir import GDMkdir
from gdcmdtools.find import GDFind

from apiclient import errors


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

        # get title and check if folder, is_folder and title are available now
        self.is_folder = None
        self.title = None

        self.get_file_meta()

        self.copy_dir_stat = {
            "total":0}

    def get_file_meta(self):
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

            self.is_folder = (raw == folder_mime)
            self.title = response['title']
            if not self.parent_id:
                self.parent_id = response["parents"][0]["id"]


    def run(self):

        if self.new_title:
            self.title = self.new_title

        if self.parent_id is None:
            parents=[]
        else:
            parents=[{
                "kind": "drive#fileLink",
                "id": self.parent_id}]

        body={
            'title': self.title,
            'description': self.target_description,
            'parents': parents}

        logger.debug("is_folder: %s", self.is_folder)

        try:
            if self.is_folder:
                class args():
                    copy_mode = True
                    parent_id = self.parent_id
                    folder_id = self.id
                    new_title = self.new_title

                find = GDFind(args)
                response=find.find(args.folder_id, find.title_folder, args.parent_id, args.copy_mode, find.tree)

            else:
                response=self.service.files().copy(fileId=self.id, body=body).execute()
        except Exception as e:
            logger.error(e)
            raise
        else:
            return self.is_folder, response
