#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from base import GDBase
import logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

from gdcmdtools.auth import GDAuth

import requests
import re
import os

import pprint

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
            logger.debug(result_title_format)

            title, return_format = result_title_format
            if self.format != "raw":
                title = title +"." +self.format

            if self.format not in return_format.keys():
                raise Exception("The specified format \'%s\' is not allowed, available format are \"%s\", please correct option: --export_format" % (self.format, ', '.join(return_format.keys())))

            file_content = self.get_by_format(return_format[self.format])

            if self.save_as == None:
               self.save_as = title 

            with open(self.save_as, 'wb+') as f:
                f.write(file_content)

        except Exception, e:
            logger.error(e)
            raise

        return return_format


    def get(self):
        try:
            response = self.service.files().get(fileId=self.file_id).execute()
            logger.debug(pprint.pformat(response))
            return response

        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None


    def get_title_format(self, service_response):
        export_links = service_response.get('exportLinks', None)
        return_format = {}

        title = service_response.get('title',None)

        if export_links == None:
            download_link = service_response.get(u'downloadUrl', None)
            return_format["raw"] = download_link
        else:
            export_link_values = export_links.values()

            if len(export_link_values) > 0 :
                for link in export_link_values:
                    m = re.match(r'^.*exportFormat=(.*)$',link)
                    return_format[m.group(1)] = link

        return title, return_format
        
    def get_by_format(self, link):
        resp, content = self.service._http.request(link)

        if resp.status == 200:
          logger.debug('Status: %s' % resp)
          return content
        else:
          logger.error('An error occurred: %s' % resp)
          return None
