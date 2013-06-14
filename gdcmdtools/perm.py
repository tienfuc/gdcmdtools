#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from base import GDBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


permission_resource_properties = {
        "role":["owner", "reader", "writer"],
        "type":["user", "group", "domain", "anyone"]}

class GDPerm:
    def __init__(self, file_id, action):
        # base
        base = GDBase()
        creds = base.get_credentials()
        if creds == None:
            raise Exception("Failed to retrieve credentials")

        self.http = base.get_authorized_http(creds)
        self.service = base.get_drive_service()
        
        self.file_id = file_id
        self.action = action['name']
        self.param = action['param']

    def run(self):
        try: 
            result = getattr(self, self.action)()
        except Exception, e:
            logger.error(e)
            raise

    def insert(self):

        new_permission = {
                'type': self.param[0],
                'role': self.param[1], 
                'value': self.param[2],
                }

        try:
            return self.service.permissions().insert(
                    fileId=self.file_id, body=new_permission).execute()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return None



