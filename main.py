import nozbe
import json

with open('credentials.json') as fp:
    credentials = json.load(fp)
n = nozbe.Nozbe()
n.login(**credentials)