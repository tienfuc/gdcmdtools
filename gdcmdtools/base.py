#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from apiclient.discovery import build

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )

import httplib2
import pprint


__APP__ = 'gdcmdtools'
__GDAPI_VER__ = 'v2'

class GDBase(object):
    def __init__(self):
        self.drive = None
        self.http = None
        pass

    def get_credentials(self, if_oob):
        home_path = os.getenv("HOME")
        storage_file = os.path.abspath('%s/.%s.creds' % (home_path,__APP__))
        logger.debug('storage_file=%s' % storage_file)

        storage = Storage(storage_file)
        credentials = storage.get()

        if credentials is None or credentials.invalid == True:
            credentials_file = os.path.abspath(
                    '%s/.%s.secrets' % (home_path,__APP__))

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
            about = self.drive.about().get().execute()

        self.root_folder = about['rootFolderId']
    
        return self.root_folder

    def get_service(self):
        discovery_url = \
                "https://www.googleapis.com/discovery/v1/apis/{api}/{apiVersion}/rest"
        self.drive = build('drive', __GDAPI_VER__, 
                discoveryServiceUrl=discovery_url, http=self.http)

        return self.drive


