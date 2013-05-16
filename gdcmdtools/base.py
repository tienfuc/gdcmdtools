#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from apiclient.discovery import build

import httplib2
import pprint

import logging 
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_INFO = {
        "app":"gdcmdtools",
        "description":'Google Drive command line tools',
        "version":'0.0.5'}

GDAPI_VER = 'v2'
FTAPI_VER = 'v1'
DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis/{api}/{apiVersion}/rest"


class GDBase(object):
    def __init__(self):
        self.drive_service = None
        self.ft_service = None
        self.http = None
        self.root_folder = None

    def get_credentials(self, if_oob):
        home_path = os.getenv("HOME")
        storage_file = os.path.abspath(
                '%s/.%s.creds' % (home_path,BASE_INFO["app"]))
        logger.debug('storage_file=%s' % storage_file)

        try:
            with open(storage_file): pass
        except IOError:
            logger.error('storage_file: %s not exists' % storage_file)
            return None

        storage = Storage(storage_file)
        credentials = storage.get()

        if credentials is None or credentials.invalid == True:
            credentials_file = os.path.abspath(
                    '%s/.%s.secrets' % (home_path,BASE_INFO["app"]))

            logger.debug('credentials_file=%s' % credentials_file)

            
            if if_oob:
                redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            else:
                redirect_uri = None

            flow = flow_from_clientsecrets(
                credentials_file,
                scope=[
                    # if using /drive.file instead of /drive,
                    # then the fusion table is not seen by drive.files.list()
                    # also, drive.parents.insert() fails.
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/fusiontables'
                    ],
                redirect_uri=redirect_uri)

            if if_oob:
                auth_uri = flow.step1_get_authorize_url()
                logger.info('Please visit the URL in your browser: %s' % auth_uri)
                code = raw_input('Insert the given code: ')

                credentials = flow.step2_exchange(code)
                storage.put(credentials)
                credentials.set_store(storage)

            else:
                credentials = run(flow, storage)

        return credentials

    def get_authorized_http(self, creds):
        self.http =  httplib2.Http()
        creds.authorize(self.http)
        wrapped_request = self.http.request

        # FIXME
        def _Wrapper(uri, method="GET", body=None, headers=None, **kw):
            logger.debug('Req: %s %s' % (uri, method))
            logger.debug('Req headers:\n%s' % pprint.pformat(headers))
            logger.debug('Req body:\n%s' % pprint.pformat(body))
            resp, content = wrapped_request(uri, method, body, headers, **kw)
            logger.debug('Rsp headers:\n%s' % pprint.pformat(resp))
            logger.debug('Rsp body:\n%s' % pprint.pformat(content))
            return resp, content

        self.http.request = _Wrapper
        return self.http

    def get_root(self):
        if self.root_folder == None:
            if self.drive_service == None:
                self.get_drive_service()
            about = self.drive_service.about().get().execute()
       
        self.root_folder = about['rootFolderId']
        logger.debug("root_folder=%s" % self.root_folder)
        return self.root_folder

    def get_drive_service(self):
        self.drive_service = build('drive', GDAPI_VER, 
                discoveryServiceUrl=DISCOVERY_URL, http=self.http)

        return self.drive_service

    def get_ft_service(self):
        self.ft_service = build('fusiontables', FTAPI_VER, 
                discoveryServiceUrl=DISCOVERY_URL, http=self.http)

        return self.ft_service


