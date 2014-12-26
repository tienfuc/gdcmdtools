#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cmd2 import cmd, make_option, options
import pdb

class gdcmd(cmd.Cmd):
    """ xxx """
    def do_quit(self, line):
        return True

    @options([
            make_option('-f', '--export_format', metavar='FORMAT', default='raw', help='specify the export format for downloading,\ngoogle_format: export_format\n%s' ),
            make_option('-s', '--save_as', metavar='NEW_FILE_NAME', help='save the downloaded file as '),
            ],
            arg_desc="file_id")

    def do_get(self, file_id, opts=None):
        """Get the file with specified id"""
        print file_id
        print opts





if __name__ == '__main__':
    gdcmd().cmdloop()


        

