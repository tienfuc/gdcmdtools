#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
from apiclient.http import MediaFileUpload
import apiclient.errors
import urllib
import requests
import json
import pprint

import logging
logger = logging.getLogger("gdput")
#logger.setLevel(logging.ERROR)

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth

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
            ['doc', 'docx', 'html', 'htm', 'txt', 'rtf']],
        'gas':[
            "GAS project",
            ['json']],
        }


# FIXME: naming
class GDPut:
    def __init__(self, **kwargs):

        logger.debug(kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.file_id = None
        self.ft_headers = None

        self.csv_latlng_suffix = "_latlng_%04x.csv" % random.getrandbits(16)

        # base
        auth = GDAuth()
        creds = auth.get_credentials()
        self.auth_user = creds.id_token.get("email",None)
        if creds == None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

        # ft service
        if self.target_type == "ft":
            self.ft_service = base.get_ft_service(self.http)
 

    def if_folder_writable(self):
        try:
            permissions = self.service.permissions().list(fileId=self.folder_id).execute()
            valid_roles = ["writer", "owner"]
            logger.debug(pprint.pformat(permissions))
            for p in permissions["items"]:
                email = p.get("emailAddress",None).lower()
                role = p.get("role",None).lower()

                logger.debug("email: %s, role: %s" % (email, role))

                if( email == self.auth_user ) and (role in valid_roles):
                    return True
        except:
            return False

        return False
        
    def run(self):
        # check folder_id
        if self.folder_id:
            if self.if_folder_writable() == False:
                raise Exception("folder_id doesn't exist or insufficient permission: %s" % self.folder_id)

        try:
            result = getattr(self, self.target_type+"_put")()
        except AttributeError as e:
            logger.error(e)
            raise 
        except Exception, e:
            logger.error(e)
            raise
            
        return result

    def get_current_user(self):
        pass

    def raw_put(self):
        return self.generic_put(False)

    def check_gas(self):
        # have "id",
        # have at least one file
        # the file should have type, id, name items.
        with open(self.source_file, "rb") as f:
            jsons = json.loads(f.read())
            
            if_ok = False

            if type(jsons) != dict:
                return False
            
            self.file_id = jsons["id"]
            if jsons["id"] and (len(jsons["files"]) > 0):
                for j in jsons["files"]:
                    if j["type"] and j["id"] and j["name"]:
                        if_ok = True
                    else:
                        return False
                        
        return if_ok 

    def gas_pack(self):
        map_type_ext = {"server_js":"js", "html":"html"}
        json_packed = {}
        try:
            with open(self.source_file, "rb") as fr1:
                jsons = json.loads(fr1.read())
                
                path = os.path.split(self.source_file)[0]
                for j in jsons["files"]:
                    file_name = os.path.join(path, "%s.%s" % (j["name"], map_type_ext[j["type"]]))
                    with open(file_name, "rb") as fr2:
                        file_content = fr2.read()

                    j["source"] = file_content

                new_json = "%s.packed" % self.source_file
                with open(new_json, "wb+") as fw:
                    fw.write(json.dumps(jsons, indent=4))
        except:
            return False
        else:
            return True

    def gas_put(self):
        if not self.check_gas():
            raise Exception("The target file is not a GAS project json, if you like to raw-upload a json, try '-t raw'")

        if not self.gas_pack():
            raise Exception("Failed to pack the GAS project files")
        
        return self.generic_put(True, file_name = "%s.packed" % self.source_file)

    def check_csv(self):
        self.csv_delimiter = ','
        with open(self.source_file, 'rb') as csv_file:
            try:    
                dialect = csv.Sniffer().sniff(csv_file.readline())
                if dialect.delimiter == self.csv_delimiter:
                    return True 
            except:
                logger.error("Failed at calling csv.Sniffer().sniff)")
        
        return False

 
    def csv_save_latlng(self):
        rows = []
        # read csv header 
        with open(self.source_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            self.ft_headers = csv_reader.next()
            
            if self.location_column and self.latlng_column:
                self.ft_headers.append(self.latlng_column)
                rows.append(self.ft_headers)
            
            # TODO: check if location in the list
            index_latlng = self.ft_headers.index(self.latlng_column)
            index_location = self.ft_headers.index(self.location_column)

            for row in csv_reader:
                latlng = self.ft_geocoding(row[index_location])
                row.insert(index_latlng, latlng)
                rows.append(row)
 
        # logger.debug(rows)

        # save new file
        csv_file_dir = os.path.dirname(self.source_file)    
        csv_file_basename = os.path.basename(self.source_file)
        csv_file_noextension = os.path.splitext(csv_file_basename)[0]
        latlng_file = os.path.join(csv_file_dir, csv_file_noextension + self.csv_latlng_suffix)
        # write csv header with latlng
        with open(latlng_file, 'wb+') as csv_file:
            csv_writer = csv.writer(csv_file, lineterminator='\n')
            csv_writer.writerows(rows)
        
        return latlng_file


    def ss_put(self):
        if not self.check_csv():
            raise Exception("The delimiter of the source csv file is not '%s'" % self.csv_delimiter)
        
        return self.generic_put(True)

    def user_define_column(self, cols, csv_column_define):
        return_cols = []
        for (col,col_type) in zip(cols, self.csv_column_define):
            d = {"type":col_type, "name":col}
            return_cols.append(d)
        
        return return_cols

    # read csv and convert to the fusion table
    def create_ft(self, target_file):
        table = {
                "name":self.title,
                "description":self.description,
                "isExportable":True,    # FIXME
                "columns":[]
                }

        with open(target_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            cols = csv_reader.next()
            
            self.ft_headers = cols            

            # FIXME:
            if self.location_column and self.latlng_column:
                if self.location_column not in cols:
                    raise Exception("Column %s not found in the csv file" % self.location_column)

                if self.csv_column_define == None: 
                    for c in cols:
                        if c == self.latlng_column:
                            d = {"type":"LOCATION"}
                        else:
                            d = {"type":"STRING"}
                        d["name"] = c

                        table["columns"].append(d)
                else:
                    table["columns"] = self.user_define_column(cols, self.csv_column_define)

            elif self.location_column and not self.latlng_column: 
                if self.location_column not in cols:
                    raise Exception("Column %s not found in the csv file" % self.location_column)
                if self.csv_column_define == None:
                    for c in cols:
                        if c == self.location_column:
                            d = {"type":"LOCATION"}
                        else:
                            d = {"type":"STRING"}
                        d["name"] = c

                        table["columns"].append(d)
                else:
                    table["columns"] = self.user_define_column(cols, self.csv_column_define)
                        

            else:

                if self.csv_column_define == None: 
                    for c in cols:
                        d = {"type":"STRING", "name":c}
                        table["columns"].append(d)
                else:
                    table["columns"] = self.user_define_column(cols, self.csv_column_define)

        return table 


    def ft_put(self):
        if not self.check_csv():
            raise Exception("The delimiter of the source csv file is not '%s'" % self.csv_delimiter)

        # save new csv file with latlng data
        if self.location_column and self.latlng_column:
            target_file = self.csv_save_latlng()
            table = self.create_ft(target_file)
        else:
            table = self.create_ft(self.source_file)
        #logger.debug('body=%s' % body)

        # table columns are created, get tableId
        service_response = self.ft_service.table().insert(body=table).execute()
        #logger.debug("service_response=%s" % service_response)
        table_id = service_response["tableId"]

        # move to target folder
        if self.folder_id != None:
            new_parent = {'id': self.folder_id}

            try:
                self.service.parents().insert(fileId=table_id, body=new_parent).execute()
            except apiclient.errors.HttpError, error:
                raise Exception('An error occurred: %s' % error)

            # remove from root folder
            try:
                self.service.parents().delete(fileId=table_id, parentId=self.root).execute()
            except apiclient.errors.HttpError, error:
                raise Exception('Atable_idn error occurred: %s' % error)
        
        if self.location_column and self.latlng_column:
            url = self.ft_put_body(table_id, target_file)
        else:
            url = self.ft_put_body(table_id, self.source_file)

        if self.permission != None:
            GDPerm.insert(self.service, service_response['tableId'], self.permission)

        ft_url = "https://www.google.com/fusiontables/data?docid=%s" % table_id

        return ft_url

    
    def ft_put_body(self, table_id, target_file):
        params = urllib.urlencode({'isStrict': "false"})
        URI = "https://www.googleapis.com/upload/fusiontables/v1/tables/%s/import?%s" % (table_id, params)
        METHOD = "POST"

        with open(target_file) as ft_file:
            # get the rows
            #ft_file.next()
            rows = ft_file.read()
            i_newline = rows.index('\n')+1
            rows = rows[i_newline:]
            # weird issue here: the URI should be encoded with UTF-8 if body is UTF-8 too.
            utf8_body = rows.decode('utf-8').encode('utf-8')
            #logger.debug(utf8_body)
            try:
                response, content = self.http.request(URI.encode('utf-8'), METHOD, body=utf8_body)
            except:
                raise Exception('Failed at calling http.request(%s, %s, %s)'
                        % (URI.encode('utf-8'), METHOD, utf8_body))

            content = json.loads(content)
            #logger.debug(content)


    @staticmethod
    def ft_geocoding(address):
        GEOCODING_URL = "http://maps.googleapis.com/maps/api/geocode/json"

        params = {'address':address, 'sensor':'false'}
        response = requests.get(GEOCODING_URL, params=params)
        response_json = (response.json())

        # FIXME
        lat = response_json["results"][0]["geometry"]["location"]["lat"]
        lng = response_json["results"][0]["geometry"]["location"]["lng"]

        latlng = str(lat)+","+str(lng)

        return latlng

    def generic_put(self, if_convert, file_name=None):
        if( file_name ):
            self.source_file = file_name
        
        media_body = MediaFileUpload(
                self.source_file, 
                mimetype=self.mime_type, 
                resumable=True)
       
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
 
        # FIXME: should impliment both update and insert for gas and non-gas file
        if self.target_type == "gas":
            request = self.service.files().update(body=body, fileId=self.file_id, media_body=media_body, convert=if_convert)
        else:
            if( self.replace_id ):
                request = self.service.files().update(body=body, media_body=media_body, convert=if_convert, fileId=self.file_id)
            else:
                request = self.service.files().insert(body=body, media_body=media_body, convert=if_convert)

        service_response = None
    
        print "Uploading file: %s" % self.source_file
        while service_response is None:
            status, service_response = request.next_chunk(num_retries=10)
            if status:
                sys.stdout.write("\rCompleted: %.2f%%" % (status.progress() * 100))
                sys.stdout.flush()
            else:
                sys.stdout.write("\rCompleted!%s\n" % (" "*10))
                sys.stdout.flush()

                if self.permission != None:
                    GDPerm.insert(self.service, service_response['id'], self.permission)

                return service_response

    def pt_put(self):
        return self.generic_put(True)

    def dr_put(self):
        return self.generic_put(True)

    def ocr_put(self):
        return self.generic_put(True)

    def doc_put(self):
        return self.generic_put(True)
        #raise Exception("this function is not supported yet")
