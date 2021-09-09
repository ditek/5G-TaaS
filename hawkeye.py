import json
import requests
from enum import Enum
import datetime

# For debugging, the script can run on a local server. See `server.py`.
run_locally = False
base_url = 'http://20.20.20.232/api/'
local_url = 'http://localhost:8888/'


###############################################################################
###############################################################################


class URL(Enum):
    login = 'login'
    tests = 'tests'
    test_results = 'testsresults'
    probes = 'probes'

    def get(self):
        return base_url + self.value


class TestStatus(Enum):
    all = 'all'
    active = 'active'
    finished = 'finished'


class ProbeStatus(Enum):
    up = 'up'
    down = 'down'


class Probe(Enum):
    '''A list of available probes. Obtained from Hawkeye's probes page.'''
    diaa_macbook = 180  # Diaas-MacBook-Pro.local
    diaa_samsung = 67  # Samsung-SM-G970F


###############################################################################
###############################################################################

def login() -> dict:
    name = '5gvinni'
    password = 'testing'
    body = {
        'username': name,
        'password': password,
    }
    r = requests.post(URL.login.get(), data=body)
    if r.status_code != 200:
        print('ERROR - Unsuccessful request: ', r)
        return {}
    if 'PHPSESSID' not in r.cookies:
        print('ERROR - No cookie: ', r.cookies)
    print('Login:', r.text)
    return r.cookies.get_dict()


def get_tests(login_cookie: dict, status: TestStatus = None, limit: int = None):
    params = {}
    if status:
        params['status'] = status.value
    if limit:
        params['status'] = limit
    r = requests.get(URL.tests.get(), params=params, cookies=login_cookie)
    print(r)


def start_test(login_cookie: dict, fromProbe: Probe, toProbe: Probe, testId: int = 5129):
    '''
    Start a test with the provided parameters.
    `testId` is not documented and is obtained by capturing the POST request
    when starting a test in the browser.
    '''
    request_body = {
        "identifier": "",
        "isMesh": 0,
        "testtypeId": testId,
        "fromProbeId": fromProbe.value,
        "toProbeId": toProbe.value,
        "fromIps": "default",
        "toIps": "default",
        "enforceSchedule": 0,
        "frequency": 0,
        "testTemplateExecutionId": 0,
        "startDate": f"{get_time()}",
        "endDate": f"{get_time()}",
        "topology": "NodeToNode",
        "callFromUI": "1",
        "parameters": {
            "basic": [
                {
                    "id": 1,
                    "name": "testduration",
                    "value": "30 sec"
                },
                {
                    "id": 105,
                    "name": "QOS",
                    "value": "BestEffort"
                }
            ]
        }
    }
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    j = json.dumps(request_body)
    r = requests.post(URL.tests.get(), data=j, headers=headers, allow_redirects=False, cookies=login_cookie)
    print(r.text)
    print(r)


def get_test_results(login_cookie: dict, limit: int = None):
    params = {}
    if limit:
        params['status'] = limit
    r = requests.get(URL.tests.get(), params=params, cookies=login_cookie)
    print(r)


def get_probes(login_cookie: dict, status: ProbeStatus = None, limit: int = None):
    params = {}
    if status:
        params['status'] = status.value
    if limit:
        params['status'] = limit
    r = requests.get(URL.tests.get(), params=params, cookies=login_cookie)
    print(r)


def get_time():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


###############################################################################
###############################################################################


if __name__ == '__main__':
    login_cookie = {}
    if run_locally:
        base_url = local_url
    else:
        login_cookie = login()
    # get_probes(login_cookie, status=ProbeStatus.up)
    # get_test_results(login_cookie, limit=10)
    # get_tests(login_cookie, status=TestStatus.active)
    start_test(login_cookie, fromProbe=Probe.diaa_samsung, toProbe=Probe.diaa_macbook)
