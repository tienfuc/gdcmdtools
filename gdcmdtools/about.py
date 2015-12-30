#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys
import urllib
import requests
import json
import pprint
import re

import logging
logger = logging.getLogger("gdabout")

import random
import os

import json

from gdcmdtools.base import GDBase
from gdcmdtools.perm import GDPerm
from gdcmdtools.auth import GDAuth

class GDAbout:

    def __init__(self, args):

        for key, value in vars(args).items():
            setattr(self, key, value)

        auth = GDAuth()

        creds = auth.get_credentials()
        self.auth_user = creds.id_token.get("email", None)

        if creds is None:
            raise Exception("Failed to retrieve credentials")
        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        self.root = base.get_root()

    def run(self):

        try:
            response = self.service.about().get().execute()
        except Exception as e:
            logger.error(e)
            raise
        else:
            return response
