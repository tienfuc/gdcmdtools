#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import unittest
import os
import subprocess
import filecmp


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_00_if_travis(self):
        if os.environ.get('TRAVIS', None) == "true":
            Test.if_travis = True
        else:
            Test.if_travis = False

    def test_01_get_secret(self):
        if Test.if_travis == False:
            return True

        client_id = os.environ['client_id']
        client_secret = os.environ['client_secret']
        
        secret_example_file = "./samples/gdcmdtools.secrets.EXAMPLE"
        
        with open(secret_example_file) as f:
            secret_example = f.read()
            
        new_secret_1 = re.sub(r'"client_id":"X"',r'"client_id":"%s"' % client_id, secret_example, flags=re.MULTILINE)
        new_secret = re.sub(r'"client_secret":"X"',r'"client_secret":"%s"' % client_secret, new_secret_1, flags=re.MULTILINE)

        Test.secret_file = os.path.expanduser("~/.gdcmdtools.secrets")

        with open(Test.secret_file,'w') as f:
            f.write(new_secret)

        assert True

    def test_01_get_credentials(self):
        if Test.if_travis == False:
            return True

        client_id = os.environ['client_id']
        client_secret = os.environ['client_secret']
        access_token = os.environ['access_token']
        refresh_token = os.environ['refresh_token']
        
        credentials_example_file = "./samples/gdcmdtools.creds.EXAMPLE"
        
        with open(credentials_example_file) as f:
            credentials_example = f.read()
            
        new_credentials_id = re.sub(r'"client_id":"X"',r'"client_id":"%s"' % client_id, credentials_example, flags=re.MULTILINE)
        new_credentials_secret = re.sub(r'"client_secret":"X"',r'"client_secret":"%s"' % client_secret, new_credentials_id, flags=re.MULTILINE)
        new_credentials_token = re.sub(r'"access_token":"X"',r'"access_token":"%s"' % access_token, new_credentials_secret, flags=re.MULTILINE)
        new_credentials = re.sub(r'"refresh_token":"X"',r'"refresh_token":"%s"' % refresh_token, new_credentials_token, flags=re.MULTILINE)

        Test.credentials_file = os.path.expanduser("~/.gdcmdtools.creds")

        with open(Test.credentials_file,'w') as f:
            f.write(new_credentials)
        
        assert True

    def test_10_raw_put(self):
        files = {"./samples/sample.txt":0, "":2, "x":1}

        for file, code in files.iteritems():
            cmd_debug = "python ./gdput.py --debug debug -t raw %s" % file
            print "Run %s> %s" % ("-"*30, cmd_debug)
            
            try:
                response = subprocess.check_output(cmd_debug, shell=True)
                m = re.search("id: (.*)", response, re.MULTILINE)

                assert m

                if m:
                    Test.raw_file_id = m.group(1)
                    assert True
                else:
                    assert False

            except subprocess.CalledProcessError, e:
                assert (e.returncode == code) 

    def test_11_raw_get(self):
        files = {Test.raw_file_id:0, "":2, "x":1}

        for file_id, code in files.iteritems():
            file_ori = file_id
            file_get = "/tmp/gdcmdtools.tmp"
            cmd_debug = "python ./gdget.py --debug debug -f raw -s %s %s" % (file_get, file_id)
            print "Run %s> %s" % ("-"*30, cmd_debug)

            try:
                response = subprocess.check_output(cmd_debug, shell=True)
                if os.path.isfile(file_ori):
                    result = filecmp.cmp(file_ori, file_get)
                    assert result

            except subprocess.CalledProcessError, e:
                assert (e.returncode == code)


    def test_12_converted_put(self):
        file = "./samples/sample.txt"
        cmd = "python ./gdput.py -t doc %s" % file
        cmd_debug = "python ./gdput.py --debug debug -t doc %s" % file
        print "Run %s> %s" % ("-"*30, cmd_debug)
        
        try:
            response = subprocess.check_output(cmd_debug, shell=True)
        except subprocess.CalledProcessError, e:
            assert e.returncode

        m = re.search("id: (.*)", response, re.MULTILINE)

        assert m
        if m:
            Test.converted_file_id = m.group(1)
            assert True
        else:
            assert False

    def test_20_gas_put(self):
        file = "./samples/gas/gas.json"
        cmd = "python ./gdput.py -t gas --gas_new %s" % file
        cmd_debug = "python ./gdput.py --debug debug -t gas --gas_new %s" % file
        print "Run %s> %s" % ("-"*30, cmd_debug)
        
        try:
            response = subprocess.check_output(cmd_debug, shell=True)
        except subprocess.CalledProcessError, e:
            assert e.returncode

        m = re.search("id: (.*)", response, re.MULTILINE)
        #print response
        #print m.group(1)
        assert m
        if m:
            Test.gas_file_id = m.group(1)
            assert True
        else:
            assert False

    def test_21_gas_get(self):

        assert Test.gas_file_id

        if Test.gas_file_id:
            file_ori = "./samples/gas/Code.js"
            file_get = "./Code.js"
            cmd_debug = "python ./gdget.py --debug debug -f json %s" % (Test.gas_file_id)
            print "Run %s> %s" % ("-"*30, cmd_debug)

            try:
                response = subprocess.check_output(cmd_debug, shell=True)
            except subprocess.CalledProcessError, e:
                assert e.returncode

            result = filecmp.cmp(file_ori, file_get)

            assert result
        else:
            assert False

    def test_30_mkdir(self):
        dir_name = "a dir"
        cmd_debug = "python ./gdmkdir.py --debug debug \"%s\"" % dir_name
        print "Run %s> %s" % ("-"*30, cmd_debug)

        try:
            response = subprocess.check_output(cmd_debug, shell=True)
        except subprocess.CalledProcessError, e:
            assert e.returncode

        m = re.search("id: (.*)", response, re.MULTILINE)

        assert m 
        
        if m:
            Test.dir_file_id = m.group(1)
            assert True
        else:
            assert False
        

    def test_31_rm(self):
        cmd_debug = "python ./gdrm.py --debug debug %s" % Test.dir_file_id
        print "Run %s> %s" % ("-"*30, cmd_debug)

        try:
            response = subprocess.check_output(cmd_debug, shell=True)
        except subprocess.CalledProcessError, e:
            assert e.returncode

        assert True


    def test_99_cleanup(self):
        if Test.if_travis == False:
            return True

        try:
            os.remove(Test.secret_file)
            os.remove(Test.credentials_file)
        except:
            assert False
        else:
            assert True

if __name__ == '__main__':
    unittest.main()
