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
        self.title_folder = response["title"]

        parent = response.get("parents",None)
        if len(parent) > 0:
            self.id_parent = parent.get("id",None)
        else:
            self.id_parent = None

        # statistics
        self.stats = []

        # tree
        self.tree = OrderedDict()
        self.tree["root"] = {}


    def find(self, folder_id, title_folder, id_parent, copy_mode, current_node):
        # make new folder
        mime_folder = "application/vnd.google-apps.folder"
        body_folder = {
            'title': title_folder,
            'mimeType': mime_folder
            }

        if id_parent:
            body_folder['parents'] = [{
                "id": id_parent,
                "kind": "drive#fileLink"}]

        response_new_parent = self.service.files().insert(body=body_folder).execute()
        id_new_parent = response_new_parent["id"]

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

                current_node[title_folder] = {}

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

                        # save to tree
                        current_node[title_folder][title] = {}

                    parent_id = folder_id

                    logger.debug("title: %20s, mime: %15s, id:%s\n%sparent_id:%s"%(title[:20], mime_short[:15], file_id, " "*45, parent_id))

                    if mime_short == '.folder':
                       # recursive
                        self.find(file_id, title, id_new_parent, copy_mode, current_node[title_folder][title])
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

                                stat = {
                                        "id":file_id,
                                        "title":title,
                                        "id_parent":parent_id,
                                        "cp_status":status}

                                self.stats.append(stat)

                page_token=children.get('nextPageToken')

                if not page_token:
                    break

            except:
                raise

        return self.tree

    def run(self):

        try:
            response = self.find(self.folder_id, self.title_folder, self.id_parent, self.copy_mode, self.tree["root"])

        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
