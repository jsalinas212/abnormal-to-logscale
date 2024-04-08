#!/bin/python3

######################################################################################
# This script is meant to query API data from the Abnormal Security API and feed
# it to LogScale's ingest API.
#
# Version: 0.01.4
######################################################################################

import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

srcUrl = "https://api.abnormalplatform.com/v1/"

srcToken = os.environ.get('SRCTOKEN') # Get auth token from environment variable

srcHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + str(srcToken)
}

coTenant = os.environ.get('COTENANT')
dstUrl = str(coTenant) + ".ingest.logscale.us-1.crowdstrike.com/api/v1/ingest/json"

dstToken = os.environ.get('DSTTOKEN')

dstHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + str(dstToken)
}

sTime = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
pTime = (datetime.datetime.now(datetime.UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")

endpoints = {
    "cases",
    "vendor-cases",
    "abusecampaigns"
}

def siemFeed(jsonData):
    req = requests.post(dstUrl, headers=dstHeaders, json=jsonData)
    res = req.status_code

    print(str(res) + "\n\n" + str(req))

def nePayload(ep, code):
    payload = {
        "timestamp": pTime,
        "api_endpoint": ep,
        "code": code,
        "msg": "no events found",
        "test_method": "python script",
        "script_name": "abnormal-to-logscale.py",
        "script_version": "0.01.4",
    }

    siemFeed(payload)

def doNothing():
    pass

def getEventDetails(ep, events):
        catId = list(events)[0]
        eventId = events[catId]

        if not eventId:
            doNothing()
        else:
            url = srcUrl+ep+"/"+str(eventId)
        
        req = requests.get(url, headers=srcHeaders)
        jsonData = req.json()

        siemFeed(jsonData)

def getEvents(ep, params):
    req = requests.get(srcUrl+ep, headers=srcHeaders, params=params)
    res = req.json()
    # code = req.status_code # For testing
    cat = list(res)[0]

    for events in res[cat]:
        match ep:
            case "cases":
                doNothing() if not res[cat] else getEventDetails(ep, events) # Normally doNothing() or nePayload(ep, code) for testing
            case "vendor-cases":
                doNothing() if not res[cat] else getEventDetails(ep, events) # Normally doNothing() or nePayload(ep, code) for testing
            case "abusecampaigns":
                doNothing() if not res[cat] else getEventDetails(ep, events) # Normally doNothing() or nePayload(ep, code) for testing               

def getReqs(ep):

    match ep:
        case "cases":
            paramOpts = "createdTime"
        case "vendor-cases":
            paramOpts = "firstObservedTime"
        case "abusecampaigns":
            paramOpts = "lastReportedTime"
        case _:
            exit() 

    params = {
        "filter": paramOpts + " gte " + sTime,
        "pageSize": 5
    }

    getEvents(ep, params)

for endpoint in endpoints:
    getReqs(endpoint)