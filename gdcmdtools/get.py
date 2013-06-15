#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from base import GDBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


import requests
import re
import os

class GDGet:
    def __init__(self, file_id, format, save_as):
        # base
        base = GDBase()
        creds = base.get_credentials()
        if creds == None:
            raise Exception("Failed to retrieve credentials")

        self.http = base.get_authorized_http(creds)
        self.service = base.get_drive_service()
        
        self.file_id = file_id
        self.format = format

        if save_as == None:
            self.save_as = None
        else:
            self.save_as = os.path.abspath(save_as)

    def run(self):
        try: 
            result = self.get()
            title, result_exports = self.get_title_format(result)
            file_content = self.get_by_format(result_exports[self.format])

            if self.save_as == None:
               self.save_as = title 

            with open(self.save_as, 'wb+') as f:
                f.write(file_content)

        except Exception, e:
            logger.error(e)
            raise

        return result_exports


    def get(self):

        try:
            return self.service.files().get(fileId=self.file_id).execute()
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None


    def get_title_format(self, result):
        export_links = result.get('exportLinks',[])  # FIXME
        export_link_values = export_links.values()

        return_format = {}
        if len(export_link_values) > 0 :
            for link in export_link_values:
                m = re.match(r'^.*exportFormat=(.*)$',link)
                return_format[m.group(1)] = link

        title = result.get('title',[]) + '.' + self.format

        return title, return_format
            
    def get_by_format(self, link):
        resp, content = self.service._http.request(link)

        if resp.status == 200:
          logger.debug('Status: %s' % resp)
          return content
        else:
          logger.debug('An error occurred: %s' % resp)
          return None
