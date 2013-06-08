#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors

permission_resource_properties = {
        "role":["owner", "reader", "writer"],
        "type":["user", "group", "domain", "anyone"]}

class GDPerm:
    def __init__(self, permission):
        # base
        base = GDBase()
        creds = base.get_credentials(if_oob)
        if creds == None:
            raise Exception("Failed to retrieve credentials")

        self.http = base.get_authorized_http(creds)
        self.service = base.get_drive_service()
 
        pass

 
    @staticmethod 
    def insert(service, file_id, permission):

        new_permission = {
                'type': permission[0],
                'role': permission[1], 
                'value': permission[2],
                }

        try:
            return service.permissions().insert(
                    fileId=file_id, body=new_permission).execute()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return None
