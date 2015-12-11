#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from base import GDBase
import logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

from pprint import pprint

from auth import GDAuth

permission_resource_properties = {
        "role":["owner", "reader", "writer"],
        "type":["user", "group", "domain", "anyone"]}

help_permission_text = [(j+": "+', '.join(permission_resource_properties[j])) for j in permission_resource_properties.keys()]

class GDPerm:
    def __init__(self, file_id, action):
        # base
        auth = GDAuth()
        creds = auth.get_credentials()

        if creds == None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

        self.file_id = file_id
        self.action = action['name']
        self.param = action['param']

    def run(self):
        try: 
            result = getattr(self, self.action)()
        except Exception, e:
            logger.error(e)
            raise

        return result

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
            logger.error('An error occurred: %s' % error)
        return None

    def list(self):
        try:
            permissions = self.service.permissions().list(fileId=self.file_id).execute()
            logger.debug(permissions)
            return permissions.get('items', [])
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None

    def get(self):
        try:
            permissions = self.service.permissions().get(fileId=self.file_id, permissionId=self.param).execute()
            return permissions
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None

    def delete(self):
        try:
            permissions = self.service.permissions().delete(fileId=self.file_id, permissionId=self.param).execute()
            return permissions
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None

    def get_by_user(self):
        permissions = self.list()
        user_email = self.param.lower()

        for p in permissions:
            if p.has_key("emailAddress"):
                perm_email = p["emailAddress"].lower()
                if user_email == perm_email:
                    return p

        return None
    
