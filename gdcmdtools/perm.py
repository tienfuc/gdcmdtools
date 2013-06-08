#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
# ...

permission_resource_properties = {
        "role":["owner", "reader", "writer"],
        "type":["user", "group", "domain", "anyone"]}


# permission text
# private
# anyone_w_link_read
# anyone_w_link_write
# public_read
# public_write


 
def insert_permission(service, file_id, value, perm_type, role):
  """Insert a new permission.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to insert permission for.
    value: User or group e-mail address, domain name or None for 'default'
           type.
    perm_type: The value 'user', 'group', 'domain' or 'default'.
    role: The value 'owner', 'writer' or 'reader'.
  Returns:
    The inserted permission if successful, None otherwise.
  """
  new_permission = {
          'value': value,
          'type': perm_type,
          'role': role
          }
  try:
      return service.permissions().insert(
              fileId=file_id, body=new_permission).execute()
  except errors.HttpError, error:
      print 'An error occurred: %s' % error
  return None
