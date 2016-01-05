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
        
        # get title
        response = self.service.files().get(fileId=self.folder_id).execute()
        self.title_folder = response["title"]
        self.id_parent = response["parents"][0]["id"] 


    def find(self, folder_id, title_folder, id_parent):
        # make new folder
        mime_folder = "application/vnd.google-apps.folder"
        body_folder = {
            'title': title_folder,
            'mimeType': mime_folder,
            'parents': [{
                "kind": "drive#fileLink",
                "id": id_parent}]
            }


        response_new_parent = self.service.files().insert(body=body_folder).execute()
        id_new_parent = response_new_parent["id"]
        print("new folder: %s %s %s" % (title_folder, id_new_parent, id_parent))

        page_token = None
        #print("title: %10s, mime: %12s, id:%s")%(title_folder[:10], ".folder", folder_id)
        while True:
            try:
                param = {
                        'q':"trashed = false" }

                if page_token:
                    param['pageToken'] = page_token

                children = self.service.children().list(
                        folderId=folder_id, **param).execute()

                for child in children.get('items', []):

                    file_id = child[u'id']

                    try:
                        response = self.service.files().get(fileId=file_id).execute()
                    except Exception as e:
                        logger.error(e)
                        raise
                    else:
                        title = response[u'title']
                        mime = response['mimeType']
                        mime_short = os.path.splitext(mime)[1]
                        is_trashed = response['explicitlyTrashed']

                        body_new_parent = {
                                'title': title,
                                'description': None,
                                'parents': [{
                                    "kind": "drive#fileLink",
                                    "id": id_new_parent
                                    }]
                            }


                    #logger.debug("title: %s, id: %s , file type: %s" % (title, file_id, mime))
                    parent_id = folder_id
                    if mime_short == ".folder":
                        print("title: %8s, mime: %-15s, id:%57s, p: %10s")%(title[:8], mime_short[:15], file_id, parent_id[-10:])
                    else:
                        print("title: %8s, mime: %15s, id:%57s, p: %10s")%(title[:8], mime_short[:15], file_id, parent_id[-10:])

                    if mime_short == '.fusiontable':
                        # copy with fustion table api
                        pass
                    elif mime_short == '.folder':
                        # recursive
                        self.find(file_id, title, id_new_parent )
                    else:
                        # copy it
                        self.service.files().copy(fileId=file_id, body=body_new_parent).execute()
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
            response = self.find(self.folder_id, self.title_folder, self.id_parent)

        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
