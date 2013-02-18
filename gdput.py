#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gdcmdtools.csv import GDCSV
from gdcmdtools.base import GDBase






base = GDBase()


creds = base.get_credentials(True)
http = base.get_authorized_http(creds)
drive = base.get_service()

print(drive)



csv = GDCSV()

csv.put(drive, "./example.csv")

