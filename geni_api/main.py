#!/usr/bin/env python3
import pickle
import time
import datetime

from pprint import pprint

import requests

from common import api_key, api_secret

# base_url = "http://www.geni.com/api/surname-{}/profiles"
profile_url = "https://www.geni.com/api/profile-{}"
immediate_family_url = "https://www.geni.com/api/profile-{}/immediate-family"
login_url = "https://www.geni.com/platform/oauth/request_token"
access_token = None


def save_responses(responses):
    with open("responses_output.pickle", "wb") as responses_file:
        pickle.dump(responses, responses_file, pickle.HIGHEST_PROTOCOL)

def app_login():
    request_parameters = {"client_id": api_key,
                          "client_secret": api_secret,
                          "grant_type": "client_credentials"}
    r = requests.get(login_url, params = request_parameters)
    json = r.json()
    return json["access_token"]
    

responses = []
access_token = app_login()
last_time = time.time()
i = 1
while True:
    now = time.time()
    print(now - last_time)
    last_time = now

    person_response = {"id": i,
                       "data": None,
                       "immediate_family": None}
    r = requests.get(profile_url.format(i), params = request_parameters)
    print(r.url)
    person_response["data"] = r.json()
    if "results" in person_response["data"]:
        save_responses(responses)
        break
    r = requests.get(immediate_family_url.format(i),
                     params = request_parameters)
    print(r.url)
    person_response["immediate_family"] = r.json()
    # pprint(person_response)
    responses.append(person_response)
    if i % 1000 is 0 and i > 0:
        save_responses(responses)
    i+=1
    # Sleep as a cheap form of rate limiting.
    time.sleep(0.8)


        
        
        
