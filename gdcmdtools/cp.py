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

    def copy_dir(self, txt_folder_name, id_folder, id_parent_folder):
        # make new dir
        if id_parent_folder is None:
            parents = []
        else:
            parents = [{
                "kind": "drive#fileLink",
                "id": id_parent_folder}]

        folder_mime_type = "application/vnd.google-apps.folder"

        class args:
            parent_folderId = id_parent_folder 
            folder_name = txt_folder_name
            mime_type = folder_mime_type
            target_description = self.target_description
            permission = self.permission


        mkdir = GDMkdir(args)
        
        response = mkdir.run()
        
        self.id_new_folder = response["id"]

        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token

                children = self.service.children().list(
                        folderId=id_folder, **param).execute()

                pprint.pprint(children)

                parents=[{
                    "kind": "drive#fileLink",
                    "id": self.id_new_folder}]

                body={
                    'title': None, 
                    'description': self.target_description,
                    'parents': parents}


                for child in children.get('items', []):
                    # print 'File Id: %s' % child['id']
                    file_id = child[u'id']

                    try:
                        response = self.service.files().get(fileId=file_id).execute()
                    except Exception as e:
                        logger.error(e)
                        raise
                    else:
                        body["title"] = response[u'title']
                        mime_type = response['mimeType']

                    logger.debug("title: %s, id: %s , file type: %s" % (body["title"], file_id, mime_type))

                    if mime_type == 'application/vnd.google-apps.fusiontable':
                        # copy with fustion table api
                        pass
                    elif mime_type == 'application/vnd.google-apps.folder':
                        # recursive
                        self.copy_dir(body["title"], file_id, self.id_new_folder)
                    else:
                        # copy it
                        self.service.files().copy(fileId=file_id, body=body).execute()
                    
                    self.copy_dir_stat["total"] += 1

                page_token=children.get('nextPageToken')
                if not page_token:
                    break

            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break

        return self.copy_dir_stat


    def run(self):

        if self.new_title:
            self.title = self.new_title

        if self.parent_folderId is None:
            parents=[]
        else:
            parents=[{
                "kind": "drive#fileLink",
                "id": self.parent_folderId}]

        body={
            'title': self.title,
            'description': self.target_description,
            'parents': parents}

        logger.debug("is_folder: %s", self.is_folder)

        try:
            if self.is_folder:
                response=self.copy_dir(self.title, self.id, self.parent_folderId)
            else:
                response=self.service.files().copy(fileId=self.id, body=body).execute()
        except Exception as e:
            logger.error(e)
            raise
        else:
            return self.is_folder, response
