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

from collections import OrderedDict

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
        pprint.pprint(response)
        if self.new_title:
            self.title_folder = self.new_title
        else:
            self.title_folder = response["title"]

        if self.parent_id == None:
            parents = response.get("parents",None)
            for p in parents: 
                if p.get("isRoot", False):
                    self.parent_id = p["id"]

        # statistics
        self.stats = []

        # tree
        self.tree = OrderedDict()
        self.tree["root"] = {}


    def find(self, folder_id, title_folder, parent_id, copy_mode, current_node):
        # make new folder
        mime_folder = "application/vnd.google-apps.folder"
        body_folder = {
            'title': title_folder,
            'mimeType': mime_folder
            }

        if parent_id:
            body_folder['parents'] = [{
                "id": parent_id,
                "kind": "drive#fileLink"}]

        response_new_parent = self.service.files().insert(body=body_folder).execute()
        new_parent_id = response_new_parent["id"]

        page_token = None
        while True:
            try:
                # make it optional?
                param = {
                        'q':"trashed = false" }

                if page_token:
                    param['pageToken'] = page_token

                children = self.service.children().list(
                        folderId=folder_id, **param).execute()

                if title_folder in current_node:
                    title_folder += "^"

                current_node[title_folder] = {}

                for child in children.get('items', []):

                    file_id = child[u'id']

                    if file_id == new_parent_id:
                        continue

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
                                    "id": new_parent_id
                                    }]
                            }

                    logger.debug("title: %14s, mime: %11s, id:%s\n%sparent_id:%s"%(title[:14], mime_short[:11], file_id, " "*48, folder_id))

                    if mime_short == '.folder':
                        # recursive
                        current_node[title_folder][title] = {}
                        self.find(file_id, title, new_parent_id, copy_mode, current_node[title_folder])
                    else:
                        if copy_mode:
                            if mime_short == '.fusiontable':
                                pass
                            else:
                                try:
                                    self.service.files().copy(fileId=file_id, body=body_new_parent).execute()
                                except:
                                    status = False
                                else:
                                    status = True

                        if status:
                            current_node[title_folder][title] = {}
                        else:
                            current_node[title_folder][title] = {status:{}}

                page_token=children.get('nextPageToken')

                if not page_token:
                    break

            except:
                raise

        return self.tree

    def run(self):

        try:
            response = self.find(self.folder_id, self.title_folder, self.parent_id, self.copy_mode, self.tree["root"])

        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
