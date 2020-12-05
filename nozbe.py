#
# -*- coding: utf-8 -*-
import logging
import os

import requests
import json

log = logging.getLogger("nozbe")


class Nozbe(object):
    API_URL = 'https://api.nozbe.com:3000'
    SESSION = None

    def __init__(self):
        if self.SESSION is None:
            self.SESSION = requests.Session()

    def login(self, username=None, password=None):
        if not self._get_application(username, password):
            self._create_application(username,password)

    def _decode_credentials(self, data):
        self.CLIENT_ID = data['client_id']
        self.CLIENT_SECRET = data['client_secret']


    def _create_application(self, email, password):
        url = f"{self.API_URL}{'/oauth/secret/create'}"
        post = {"email" : email, "password" : password, "redirect_uri" : "http://example.com"  }
        r = self.SESSION.get(url, params=post)
        if r.status_code == 200:
            self._decode_credentials(r.json())
            return True
        return False

    def _get_application(self, email, password):
        url = f"{self.API_URL}{'/oauth/secret/data'}"
        post = {"email" : email, "password" : password }
        r = self.SESSION.get(url, params=post)
        if r.status_code == 200:
            self._decode_credentials(r.json())
            return True
        return False

