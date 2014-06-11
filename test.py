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

    def test_00_get_secret(self):
        client_id = os.environ['CLIENT_ID']
        client_secret = os.environ['CLIENT_SECRET']
        
        secret_example_file = "./samples/gdcmdtools.secrets.EXAMPLE"
        
        with open(secret_example_file) as f:
            secret_example = f.read()
            
        new_secret_1 = re.sub(r'"client_id":"X"',r'"client_id":"%s"' % client_id, secret_example, flags=re.MULTILINE)
        new_secret = re.sub(r'"client_secret":"X"',r'"client_secret":"%s"' % client_secret, new_secret_1, flags=re.MULTILINE)

        secret_file = "./gdcmdtools.secret"

        with open(secret_file,'w') as f:
            f.write(new_secret)
        
        cmd_debug = "python ./gdauth.py %s" % secret_file
        return_value = subprocess.call(cmd_debug, shell=True)
        os.remove(secret_file)
        
        if return_value == 0:
            assert True
        else:
            assert False

    def test_01_raw_put(self):
        file = "./samples/sample.txt"
        cmd = "python ./gdput.py -t raw %s" % file
        cmd_debug = "python ./gdput.py --debug debug -t raw %s" % file
        
        response = subprocess.check_output(cmd, shell=True)
        m = re.search("id: (.*)", response, re.MULTILINE)
        print response
        print m.group(1)
        if m:
            Test.raw_file_id = m.group(1)
            assert True
        else:
            assert False

    def test_02_raw_get(self):

        if Test.raw_file_id:
            file_ori = "./samples/sample.txt"
            file_get = "/tmp/gdcmdtools.tmp"
            cmd_debug = "python ./gdget.py -f raw -s %s %s" % (file_get, Test.raw_file_id)
            response = subprocess.check_output(cmd_debug, shell=True)
            result = filecmp.cmp(file_ori, file_get)

            assert result
        else:
            assert False

    def test_03_converted_put(self):
        file = "./samples/sample.txt"
        cmd = "python ./gdput.py -t doc %s" % file
        cmd_debug = "python ./gdput.py --debug debug -t doc %s" % file
        
        response = subprocess.check_output(cmd, shell=True)
        m = re.search("id: (.*)", response, re.MULTILINE)
        print response
        print m.group(1)
        if m:
            Test.converted_file_id = m.group(1)
            assert True
        else:
            assert False
    

if __name__ == '__main__':
    unittest.main()
