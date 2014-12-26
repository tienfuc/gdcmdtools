#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cmd2 import cmd, make_option, options
from gdcmdtools.get import GDGet
from gdcmdtools.get import export_format
import sys


class Gdcmd(cmd.Cmd):
    """ xxx """
    def do_quit(self, line):
        return True

    @options([
            make_option('-f', '--export_format', metavar='FORMAT', default='raw', help='specify the export format for downloading,\ngoogle_format: export_format' ),
            make_option('-s', '--save_as', metavar='NEW_FILE_NAME', help='save the downloaded file as'),
            ],
            arg_desc="file_id")

    def do_get(self, file_id, opts=None):
        """Get the file with specified id"""
        print "xxxx"
        get = GDGet(file_id, opts.export_format, opts.save_as)
        result = get.run()
    

    @options([],arg_desc="[debug|info|critical]")
    def do_debug(self, level, opts=None):
        print level



if __name__ == '__main__':
    gdcmd = Gdcmd(sys.argv)

    if len(sys.argv) > 1:
        gdcmd.onecmd(' '.join(sys.argv[1:]))
    else:
        gdcmd.cmdloop()
        

