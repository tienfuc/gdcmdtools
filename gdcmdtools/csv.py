#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from apiclient.http import MediaFileUpload
import apiclient.errors
import apiclient.http

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger( __name__ )


class GDCSV(object):

    def __init__(self):
        pass

    def put(self, drive, filename, title=None, folder_id=None, if_convert=False):
        if filename == None:
            return False

        mime = "text/csv"
         
        media_body = MediaFileUpload(filename, mimetype=mime, resumable=False)
       
        if folder_id == None:
            parents = []
        else:
            parents = [{
                "kind":"drive#fileLink",
                "id":folder_id}]

        body = {
                'title':title,
                'mimeType':mime,
                'parents':parents}
 
        logger.debug('body=%s' % body)

        try:
            service_response = drive.files().insert(
                    body=body,
                    media_body=media_body,
                    # so csv will be converted to spreadsheet
                    convert=if_convert
                    ).execute()

            logger.info("The file is located at: %s" % 
                    service_response["alternateLink"])

        except apiclient.errors.HttpError, e:
            logger.error('http error:', e)


           

