#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build

import httplib2
import pprint
import re

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_INFO = {
    "app": "gdcmdtools",
    "description": 'Google Drive command line tools',
    "version": '1.05'}

GDAPI_VER = 'v2'
FTAPI_VER = 'v1'
DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis/{api}/{apiVersion}/rest"

DEBUG_LEVEL = ('debug', 'info', 'warning', 'error', 'critical')


class GDBase(object):

    def __init__(self):
        self.drive_service = None
        self.ft_service = None
        self.http = None
        self.root_folder = None

    def get_root(self):
        if self.root_folder is None:
            if self.drive_service is None:
                self.get_drive_service()
            about = self.drive_service.about().get().execute()

        self.root_folder = about['rootFolderId']
        logger.debug("root_folder=%s" % self.root_folder)
        return self.root_folder

    def get_drive_service(self, http):
        self.drive_service = build(
            'drive',
            GDAPI_VER,
            discoveryServiceUrl=DISCOVERY_URL,
            http=http)
        return self.drive_service

    def get_ft_service(self, http):
        self.ft_service = build('fusiontables', FTAPI_VER,
                                discoveryServiceUrl=DISCOVERY_URL, http=http)
        return self.ft_service

    @staticmethod
    def get_id_from_url(url):
        # normal, https://script.google.com/d/XXXXXXXXX/edit?usp=sharing
        normal_re = "^.*/d/([\w\-]*)"
        # folder on drive url:
        # https://drive.google.com/drive/u/0/folders/XXXXXXXXXXX
        folder_url_re = "^.*/folders/([\w\-]*)"
        # folder, https://drive.google.com/folderview?id=XXXXXXXX&usp=sharing
        folder_share_re = "^.*/folderview\?id=([\w\-]*)"
        # open by id, https://drive.google.com/open?id=XXXXXXXXXX
        openbyid_re = "^.*/open\?id=([\w\-]*)"
        # webContentLink,
        # https://docs.google.com/uc?id=XXXXXXXXXX&export=download
        webcontent_re = "^.*/uc\?id=([\w\-]*)"
        # export link,
        # https://docs.google.com/feeds/download/documents/export/Export?id=XXXXXX&exportFormat=html
        export_re = "^.*/[Ee]xport\?id=([\w\-]*)"

        # general id as parameter
        id_parameter_re = "^.*\?id=([\w\-]*)"

        final_re = r"%s|%s|%s" % \
            (normal_re, folder_url_re, id_parameter_re)
        #(normal_re, folder_share_re, folder_url_re, openbyid_re, webcontent_re, export_re)
        search = re.search(final_re, url)

        if(search):
            file_id = next(x for x in search.groups() if x is not None)
        else:
            file_id = url

        logger.debug("file_id: %s" % file_id)

        return file_id
