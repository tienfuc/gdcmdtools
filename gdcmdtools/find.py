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
logger = logging.getLogger("gdfind")

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth

class GDFind:

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
        
        self.folder_id = base.get_id_from_url(self.folder_id)

    def find(self, folder_id):
        page_token = None
        while True:
            try:
                param = {
                        'q':"trashed = false" }

                if page_token:
                    param['pageToken'] = page_token

                children = self.service.children().list(
                        folderId=folder_id, **param).execute()

                #pprint.pprint(children)

                #parents=[{
                ##    "kind": "drive#fileLink",
                #    "id": self.id_new_folder}]

                #body={
                #    'title': None, 
                #    'description': self.target_description,
                #    'parents': parents}


                for child in children.get('items', []):
                    # print 'File Id: %s' % child['id']
                    file_id = child[u'id']

                    try:
                        response = self.service.files().get(fileId=file_id).execute()
                    except Exception as e:
                        logger.error(e)
                        raise
                    else:
                        title = response[u'title']
                        mime_type = response['mimeType']
                        is_trashed = response['explicitlyTrashed']

                    logger.debug("title: %s, id: %s , file type: %s" % (title, file_id, mime_type))

                    if mime_type == 'application/vnd.google-apps.fusiontable':
                        # copy with fustion table api
                        pass
                    elif mime_type == 'application/vnd.google-apps.folder':
                        # recursive
                        self.find(file_id)
                    else:
                        # copy it
                        #self.service.files().copy(fileId=file_id, body=body).execute()
                        pass
                    
                    #self.copy_dir_stat["total"] += 1

                page_token=children.get('nextPageToken')
                if not page_token:
                    break

            except:
                raise

        return None

    def run(self):

        try:
            #response = self.service.about().get().execute()
            response = self.find(self.folder_id)

        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
