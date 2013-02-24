#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from apiclient.http import MediaFileUpload

import logging
logger = logging.getLogger( __name__ )
logger.setLevel(logging.DEBUG)


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
            self, fp, source_file, mime_type, target_type, folder_id, title, if_oob):

        logger.debug("source_file=%s, mime_type=%s, target_type=%s" % 
                (source_file, mime_type, target_type))

        self.fp = fp
        self.source_file = source_file
        self.mime_type = mime_type
        self.target_type = target_type
        self.folder_id = folder_id
        self.title = title

        # base
        base = GDBase()
        creds = base.get_credentials(if_oob)
        self.http = base.get_authorized_http(creds)
        self.service = base.get_service()

    def run(self):
        try:
            result = getattr(self, self.target_type+"_put")()
        except AttributeError as e:
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
                'mimeType':self.mime_type,
                'parents':parents}
 
        try:
            service_response = self.service.files().insert(
                    body=body,
                    media_body=media_body,
                    # so csv will be converted to spreadsheet
                    convert=False
                    ).execute()
        except: 
            logger.error('http error while calling drive API: files().insert()' )
        
        return service_response


    def chk_CSV(self, fp):
        DELIMITER = ','
        dialect = csv.Sniffer().sniff(fp.readline())
        if dialect.delimiter == DELIMITER:
            return True 

        csv_file.seek(0)
        raise csv.Error("The delimiter of the source csv file is not '%s'" % DELIMITER)
        
        return False
             

    def ss_put(self):
        pass

    def ft_put(self):
        pass

    def pt_put(self):
        pass

    def dr_put(self):
        pass

    def ocr_put(self):
        pass

    def doc_put(self):
        pass
