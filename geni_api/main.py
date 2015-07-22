#!/usr/bin/env python3
import pickle
import time

from pprint import pprint

import requests

from common import api_key, api_secret

# Get a new access token 5 min before we NEED to.
LOGIN_BUFFER_TIME = 5 * 60
PROFILE_URL = "https://www.geni.com/api/profile-{}" 
IMMEDIATE_FAMILY_URL = "https://www.geni.com/api/profile-{}/immediate-family"
LOGIN_URL = "https://www.geni.com/platform/oauth/request_token"

request_parameters = {"access_token": None}
token_expire_time = None


def save_responses(responses):
    with open("responses_output.pickle", "wb") as responses_file:
        pickle.dump(responses, responses_file, pickle.HIGHEST_PROTOCOL)

def app_login():
    login_parameters = {"client_id": api_key,
                          "client_secret": api_secret,
                          "grant_type": "client_credentials"}
    r = requests.get(LOGIN_URL, params = login_parameters)
    json = r.json()
    request_parameters["access_token"] = json["access_token"]
    token_expire_time = time.time() + json["expires_in"] - LOGIN_BUFFER_TIME
    

responses = []
last_time = time.time()
i = 1
while True:
    now = time.time()
    print(now - last_time)
    last_time = now

    if token_expire_time < time.time():
        app_login()
        time.sleep(0.25)

    person_response = {"id": i,
                       "data": None,
                       "immediate_family": None}
    r = requests.get(PROFILE_URL.format(i), params = request_parameters)
    print(r.url)
    person_response["data"] = r.json()
    if "results" in person_response["data"]:
        save_responses(responses)
        break
    r = requests.get(IMMEDIATE_FAMILY_URL.format(i),
                     params = request_parameters)
    print(r.url)
    person_response["immediate_family"] = r.json()
    # pprint(person_response)
    responses.append(person_response)
    if i % 1000 is 0 and i > 0:
        save_responses(responses)
    i += 1
    # Sleep as a hacky form of rate limiting.
    time.sleep(0.7)


        
        
        
