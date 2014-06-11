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
        
        print client_id, client_secret
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
