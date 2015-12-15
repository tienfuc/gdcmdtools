#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import re
import os
import json
import io
import sys
import pprint
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import requests
from requests_oauthlib import OAuth2Session
from apiclient import errors

from gdcmdtools.auth import GDAuth
from gdcmdtools.auth import SCOPE
from base import GDBase

export_format = {
    "application/vnd.google-apps.spreadsheet":["pdf", "ods", "xlsx"],
    "application/vnd.google-apps.document":["pdf", "docx", "rtf", "odt", "html", "txt"],    
    "application/vnd.google-apps.presentation":["pdf", "pptx", "txt"],
    "application/vnd.google-apps.drawing":["png", "pdf", "jpeg", "svg"],
    "application/vnd.google-apps.script+json":["json"],
    }

class GDGet:
    def __init__(self, file_id, format, save_as):
        # base
        auth = GDAuth()
        self.credentials = auth.get_credentials()
        if self.credentials == None:
            raise Exception("Failed to retrieve credentials")

        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        
        
        file_id_from_link = re.search("^.*/d/([\w\-]*)", file_id)
        
        if file_id_from_link == None:
            self.file_id = file_id
        else:
            self.file_id = file_id_from_link.group(1)

        self.format = format

        if save_as == None:
            self.save_as = None
        else:
            self.save_as = os.path.abspath(save_as)
 
    def parse_gas_json(self, file_content, save_as):
        map_type_ext = {"server_js":"js", "html":"html"}
        try:
            jsons = json.loads(file_content)
            new_json = {"files":[]}
            for j in jsons["files"]:
                file_id = j["id"]
                file_name = j["name"]
                file_source = j["source"]
                file_type = j["type"]

                if file_type in map_type_ext.keys():
                    file_ext = map_type_ext[file_type]
                else:
                    file_ext = file_type

                file_fullname = "%s.%s" % (file_name, file_ext) 

                with open(file_fullname, 'wb+') as f:
                    f.write(file_source)
                
                j.pop("source")
                new_json["files"].append(j)

            # save the project id, we need the id to upload project
            new_json["id"] = self.file_id
            with open(save_as, 'wb+') as f:
                f.write(json.dumps(new_json, indent=4))

        except Exception, e:  
            logger.error(e)
            raise

    def run(self):
        try: 
            service_response = self.get()
            # Content-Length from http header is None
            self.file_size = service_response.get('fileSize', None)

            result_title_format = self.get_title_format(service_response)
            logger.debug(result_title_format)

            title, return_format = result_title_format
            if self.format != "raw":
                title = title +"." +self.format

            if self.format not in return_format.keys():
                raise Exception("The specified format \'%s\' is not allowed, available format are \"%s\", please correct option: --export_format" % (self.format, ', '.join(return_format.keys())))


            if self.save_as == None:
               self.save_as = title 

            if self.format == "json":
                file_content = self.get_by_format(return_format[self.format])
                self.parse_gas_json(file_content, self.save_as)               
            else:
                # FIXME: handle return value
                result, local_size = self.get_by_format(self.save_as, return_format[self.format])
                if( result == False ):
                    raise Exception("File size check failed, download may be incompleted. local size is %d" % local_size)

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

        
        logger.debug(title)
        logger.debug(export_links)

        if export_links == None:
            download_link = service_response.get(u'downloadUrl', None)
            return_format["raw"] = download_link
        else:
            export_link_values = export_links.values()

            if len(export_link_values) > 0 :
                for link in export_link_values:
                    m = re.match(r'^.*[Ff]ormat=(.*)$',link)
                    return_format[m.group(1)] = link

        return title, return_format
        
    def get_by_format(self, save_as, url):
        fd = io.FileIO(save_as, mode='wb')
        creds = self.credentials

        # move to auth.py?
        token = {"access_token":creds.access_token, "token_type":"Bearer"}
        session = OAuth2Session(creds.client_id, scope=SCOPE, token=token)

        with open(save_as, 'wb') as f:
            response = session.get(url, stream=True)
            if self.file_size:
                total_length = int(self.file_size)
                print "total size = %d Bytes" % total_length

                mega=1048576 # 1024*1024
                downloaded = 0
                total_in_mega = int(total_length/mega)

                for data in response.iter_content(chunk_size=mega):
                    f.write(data)
                    downloaded += len(data)
                    done = int(50 * downloaded / total_length)
                    done_percent = int(downloaded / total_length * 100)
                    done_in_mega = int(downloaded / mega )
                    sys.stdout.write("\r[%s%s] %3d%%, %d of %d MB" % ('=' * done, ' ' * (50-done), done_percent, done_in_mega, total_in_mega) )
                    sys.stdout.flush()
            else:
                f.write(response.content)

        # for sys.stdout.flush()
        print ""    

        # local size check
        local_size = int(os.path.getsize(save_as))
        print "File location: %s" % save_as

        if self.file_size:
            if( int(self.file_size) == local_size ):
                return True, local_size 
                print "File size: %d" % local_size
            else:
                return False, local_size
        else:
            print "File size in bytes: %d" % local_size
            return True, local_size
