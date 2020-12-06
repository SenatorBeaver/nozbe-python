#
# -*- coding: utf-8 -*-
import json
import logging
import os
from datetime import datetime
from pprint import pprint

import requests
import urllib.parse as urlparse


log = logging.getLogger("nozbe")


class Nozbe(object):
    API_URL = 'https://api.nozbe.com:3000'
    SESSION = None
    LIST_TYPES = ('task', 'project', 'context')
    RECUR_INFO = {"DoNotRepeat":0,
                  "EveryDay" : 1,
                  "EveryWeekday" : 2,
                  "EveryWeek" : 3,
                  "Every2Weeks" : 4,
                  "EveryMonth" : 5,
                  "EveryHalfYear" : 6,
                  "EveryYear" : 7,
                  "Every3Weeks" : 8,
                  "Every2Months" : 9,
                  "Every3Months" : 10,
                  "Every2Years" : 11,
                  "Every2days" : 12,
                  "Every4Weeks" : 13,
                  }

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

    def _get_authorization_header(self):
        return {"Authorization" : self.OAUTH_ACCESS_TOKEN }

    def _get_items(self, item_type):
        if not item_type in self.LIST_TYPES:
            return None
        url = f"{self.API_URL}{'/list'}"
        headers = self._get_authorization_header()
        params = dict()
        params['type'] = item_type
        r = self.SESSION.get(url, headers=headers, params=params)
        if r.status_code == 200:
            tasks = r.json()
            return tasks
        return None

    def _name_to_id(self, name:str):
        return name.lower().replace(' ', '_')

    def _set_project_by_json(self, name):
        url = f"{self.API_URL}{'/json/project'}"
        headers = self._get_authorization_header()
        project = dict()
        project['name'] = name

        r = self.SESSION.post(url, headers=headers, data=json.dumps([project]))
        if r.status_code == 200:
            response = r.json()
            ids= {val['name']:val['id'] for id,val in response.items() if 'name' in val}
            return ids[name]
        return None

    def _set_task_by_json(self, name, project_id=None, date_time:datetime=None, recur:int=None):
        url = f"{self.API_URL}{'/json/task'}"
        headers = self._get_authorization_header()
        data = dict()
        data['name'] = name
        if project_id:
            data['project_id']=project_id
        if date_time:
            data['datetime'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
        if recur:
            data['recur'] = recur
        log.debug(f"Request url: {url}, \n  headers:{headers},\n  data:{data}")
        r = self.SESSION.post(url, headers=headers, data=json.dumps([data]))
        if r.status_code == 200:
            response = r.json()
            return response
        return None

    def create_project(self, name):
        return self._set_project_by_json(name)

    def create_task(self, name, project_id=None, date_time:datetime=None, recur:int=None):
        return self._set_task_by_json(name,project_id, date_time, recur)


    def test(self):
        project_id = self.create_project('first_project')
        self.create_task('task', project_id)
        print(project_id)
        pprint(self._get_items('task'))
        pprint(self._get_items('project'))
        pprint(self._get_items('context'))