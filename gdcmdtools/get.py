#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from base import GDBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from gdcmdtools.auth import GDAuth

import requests
import re
import os

class GDGet:
    def __init__(self, file_id, format, save_as):
        # base
        auth = GDAuth()
        creds = auth.get_credentials()
        if creds == None:
            raise Exception("Failed to retrieve credentials")

        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        
        self.file_id = file_id
        self.format = format

        if save_as == None:
            self.save_as = None
        else:
            self.save_as = os.path.abspath(save_as)

    def run(self):
        try: 
            service_response = self.get()
            result_title_format = self.get_title_format(service_response)
            if result_title_format == None:
                raise Exception("The specified format \'%s\' is not allowed, please correct option: --export_format" % self.format)
            else:
                title, return_exports = result_title_format

            file_content = self.get_by_format(return_exports[self.format])

            if self.save_as == None:
               self.save_as = title 

            with open(self.save_as, 'wb+') as f:
                f.write(file_content)

        except Exception, e:
            logger.error(e)
            raise

        return return_exports


    def get(self):
        try:
            return self.service.files().get(fileId=self.file_id).execute()
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None


    def get_title_format(self, service_response):
        if service_response == None:
            return None
        else: 
            export_links = service_response.get('exportLinks',[])

        export_link_values = export_links.values()

        return_format = {}
        if len(export_link_values) > 0 :
            for link in export_link_values:
                m = re.match(r'^.*exportFormat=(.*)$',link)
                return_format[m.group(1)] = link

        if self.format in return_format.keys():
            title = service_response.get('title',[]) + '.' + self.format
            return title, return_format
        else:
            return None

            
    def get_by_format(self, link):
        resp, content = self.service._http.request(link)

        if resp.status == 200:
          logger.debug('Status: %s' % resp)
          return content
        else:
          logger.error('An error occurred: %s' % resp)
          return None
