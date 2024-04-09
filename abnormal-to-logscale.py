#!/bin/python3

######################################################################################
# This script is meant to query API data from the Abnormal Security API and feed
# it to LogScale's ingest API.
#
# Version: 0.01.5
######################################################################################

import os
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Source API settings
srcUrl = "https://api.abnormalplatform.com/v1/"
srcToken = os.environ.get('SRCTOKEN') # Get auth token from environment variable
srcHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + str(srcToken)
}


# Destination API settings
coTenant = os.environ.get('COTENANT')
dstUrl = str(coTenant) + ".ingest.logscale.us-1.crowdstrike.com/api/v1/ingest/json"
dstToken = os.environ.get('DSTTOKEN')
dstHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + str(dstToken)
}

# sTime is the search window, and pTime is the current timestamp; use datetime.datetime.nowutc() for prod due to python version
sTime = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
pTime = (datetime.datetime.now(datetime.UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")

# List of endpoints to fetch data from
endpoints = {
    "cases",
    "vendor-cases",
    "abusecampaigns"
}

# Feed events into LogScale's ingest API
def siemFeed(jsonData):
    req = requests.post(dstUrl, headers=dstHeaders, json=jsonData)
    res = req.status_code

    print(str(res))

# Test payload for when no events exist
def nePayload(ep, code):
    payload = {
        "timestamp": pTime,
        "api_endpoint": ep,
        "code": code,
        "msg": "no events found",
        "test_method": "python script",
        "script_name": "abnormal-to-logscale.py",
        "script_version": "0.01.5"
    }

    siemFeed(payload)

# Do nothing
def doNothing():
    pass

# Fetch individual event details per event
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

# Fetch list of events from each endpoint
def getEvents(ep, params):
    req = requests.get(srcUrl+ep, headers=srcHeaders, params=params)
    res = req.json()
    # code = req.status_code # For testing
    cat = list(res)[0]
    
    for events in res[cat]:
        doNothing() if not res[cat] else getEventDetails(ep, events) # Normally doNothing() or nePayload(ep, code) for testing           

# Get request parameters per endpoint
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

# Call getReqs to build parameter requirements per endpoint
for ep in endpoints:
    getReqs(ep)