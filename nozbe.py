#
# -*- coding: utf-8 -*-
import logging
import os

import requests
import urllib.parse as urlparse


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
        self._get_oauth_access_token(username, password)

    def _decode_credentials(self, data):
        self.CLIENT_ID = data['client_id']
        self.CLIENT_SECRET = data['client_secret']

    def _decode_oauth_token_from_url(self, data):
        parsed = urlparse.urlparse(data)
        items = urlparse.parse_qs(parsed.query)
        self.OAUTH_ACCESS_TOKEN = items['access_token'][0]

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

    def _get_oauth_access_token(self, username, password):
        url = f"{self.API_URL}{'/login'}"
        post = {"email": username, "password": password, "client_id" : self.CLIENT_ID, "scopes" : ''}
        r = self.SESSION.post(url, data=post)
        if r.status_code == 200:
            self._decode_oauth_token_from_url(r.request.url)
            return True
        return False
