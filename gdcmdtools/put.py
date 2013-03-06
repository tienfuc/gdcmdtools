#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from apiclient.http import MediaFileUpload
import apiclient.errors
import urllib

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


import json

from gdcmdtools.base import GDBase

DICT_OF_CONVERTIBLE_FILE_TYPE = { \
        'raw':[
            "Raw file",
            []],
        'ss':[
            "Spreadsheet",
            ['xls', 'xlsx', 'ods', 'csv', 'tsv', 'tab']],
        'ft':[
            "Fusion Table",
            ['csv']],
        'pt':[
            "Presentation",
            ['ppt', 'pps', 'pptx']],
        'dr':[
            "Drawing",
            ['wmf']],
        'ocr':[
            "OCR",
            ['jpg', 'git', 'png', 'pdf']],
        'doc':[
            "Document",
            ['doc', 'docx', 'html', 'htm', 'txt', 'rtf']]
        }

DICT_OF_REDIRECT_URI = {
    "oob":"(default) means \"urn:ietf:wg:oauth:2.0:oob\"",
    "local":"means \"http://localhost\""
    }


# FIXME: naming
class GDPut:
    def __init__(
            self, 
            source_file, 
            mime_type, 
            target_type, 
            folder_id, 
            title, 
            description, 
            if_oob):

        logger.debug("source_file=%s, mime_type=%s, target_type=%s" % 
                (source_file, mime_type, target_type))

        self.source_file = source_file
        self.mime_type = mime_type
        self.target_type = target_type
        self.folder_id = folder_id
        self.title = title
        self.description = description

        # base
        base = GDBase()
        creds = base.get_credentials(if_oob)
        self.http = base.get_authorized_http(creds)
        self.service = base.get_drive_service()
        self.root = base.get_root()

        # ft service
        if target_type == "ft":
            self.ft_service = base.get_ft_service()
            logger.debug(self.ft_service)
        # log
        
        
    def run(self):
        try:
            result = getattr(self, self.target_type+"_put")()
        except AttributeError as e:
            logger.error(e)
            raise 
        except Exception,e:
            logger.error(e)
            raise
            
        return result

    def raw_put(self):
        media_body = MediaFileUpload(
                self.source_file, 
                mimetype=self.mime_type, 
                resumable=False)
       
        if self.folder_id == None:
            parents = []
        else:
            parents = [{
                "kind":"drive#fileLink",
                "id":self.folder_id}]

        body = {
                'title':self.title,
                'description':self.description,
                'mimeType':self.mime_type,
                'parents':parents}
 
        try:
            service_response = self.service.files().insert(
                    body=body,
                    media_body=media_body,
                    # so csv will be converted to spreadsheet
                    convert=False
                    ).execute()
        except Exception,e: 
            logger.error(e)
        
        return service_response["alternateLink"]

    def chk_CSV(self):
        self.csv_delimiter = ','
        with open(self.source_file, 'rb') as csv_file:
            try:    
                dialect = csv.Sniffer().sniff(csv_file.readline())
                if dialect.delimiter == self.csv_delimiter:
                    return True 
            except csv.Error,e:
                logger.error(e)
        
        return False

    def ss_put(self):
        if not self.chk_CSV():
            raise Exception("The delimiter of the source csv file is not '%s'" % self.csv_delimiter)

        media_body = MediaFileUpload(
                self.source_file, 
                mimetype=self.mime_type, 
                resumable=False)
       
        if self.folder_id == None:
            parents = []
        else:
            parents = [{
                "kind":"drive#fileLink",
                "id":self.folder_id}]

        body = {
                'title':self.title,
                'mimeType':self.mime_type,
                'parents':parents}
 
        try:
            service_response = self.service.files().insert(
                    body=body,
                    media_body=media_body,
                    # so csv will be converted to spreadsheet
                    convert=True
                    ).execute()
        except Exception,e: 
            logger.error(e)
        
        return service_response["alternateLink"]

    # read csv and convert to the fusion table
    def create_ft(self):
        table = {
                "name":self.title,
                "description":self.description,
                "isExportable":True,    # FIXME
                "columns":[]
                }

        with open(self.source_file, 'rb') as csv_file:
            csvreader = csv.reader(csv_file)
            cols = csvreader.next()

            #TODO: sanity check for csv file
            for c in cols:
                if c == "missingRegion":
                    d = {"type":"LOCATION"}
                else:
                    d = {"type":"STRING"}
                d["name"] = c
                table["columns"].append(d)

        return table 


    def ft_put(self):
        if not self.chk_CSV():
            raise Exception("The delimiter of the source csv file is not '%s'" % self.csv_delimiter)

        """
        ftable = build('fusiontables', 'v1',
                discoveryServiceUrl=DISCOVERY_URL, http=http)
        body = create_csv_cols(args.csv_file, TITLE)
        logger.debug(body)
        """

        body = self.create_ft()
        logger.debug(body)

        # table columns are created, get tableId
        response = self.ft_service.table().insert(body=body).execute()
        logger.debug("response=%s" % response)
        table_id = response["tableId"]

        # move to target folder
        if self.folder_id != None:
            new_parent = {'id': self.folder_id}

            try:
                self.service.parents().insert(fileId=table_id, body=new_parent).execute()
            except apiclient.errors.HttpError, error:
                logger.error('An error occurred: %s' % error)

            # remove from root folder
            try:
                self.service.parents().delete(fileId=table_id, parentId=self.root).execute()
            except apiclient.errors.HttpError, error:
                logger.error('http error: %s' % error)

        # export csv rows to the fusion table
        params = urllib.urlencode({'isStrict': "false"})
        URI = "https://www.googleapis.com/upload/fusiontables/v1/tables/%s/import?%s" % (table_id, params)
        METHOD = "POST"
        
        with open(self.source_file) as ft_file:
            ft_file.readline()
            # get the rows
            rows = ft_file.read()
            # weird issue here: the URI should be encoded with UTF-8 if body is UTF-8 too.
            utf8_body = rows.decode('utf-8').encode('utf-8')
            response, content = self.http.request(URI.encode('utf-8'), METHOD, body=utf8_body)
            content = json.loads(content)


        ft_url = "https://www.google.com/fusiontables/data?docid=%s" % table_id

        return ft_url


    def pt_put(self):
        pass

    def dr_put(self):
        pass

    def ocr_put(self):
        pass

    def doc_put(self):
        pass
