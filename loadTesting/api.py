import requests
from requests.auth import HTTPBasicAuth
import asyncio
import sys
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor
import yaml
import json
import uuid
import os
import shutil
import time


class setColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Reads 'config.yaml' and loads it to be utilized
configFile = open('config.yaml')
getConfig = yaml.safe_load(configFile)

# timeit.default_timer()
START_TIME = default_timer()
# Simply generates a hash
hash = uuid.uuid4().hex

# Gets 'config.debugMode'
debugMode = getConfig['config']['debugMode']
# Concatenates 'config.baseURL' + 'categories.loadTest.tests.api.path' respectively
apiURL = getConfig['config']['baseUrl'] + getConfig['categories']['loadTest']['tests']['api']['path']
# Gets 'config.maxWorks'
getMaxWorkers = getConfig['config']['maxWorkers']

# Gets 'config.requestTimeout'
timeoutValue = getConfig['config']['requestTimeout']

# Creates '$PWD/tmp'
def createTmpDir():
    pwd = os.getcwd()
    path = os.path.join(pwd, "tmp")
    checkForExistance = os.path.exists(path)
    if checkForExistance == False:
        os.mkdir(path)

# Deletes '$PWD/tmp'
def deleteTmpDir():
    pwd = os.getcwd()
    path = os.path.join(pwd, "tmp")
    shutil.rmtree(path)

# Gets 'id' from Account payload file ($PWD/tmp/<file>.json)
def getAccountID(fileName):
    jsonFile = open(os.getcwd() + "/" + fileName)
    data = json.load(jsonFile)
    return data['id']

# Handles all API requests
def request(session, i, testName, url, requestType, requestData, outputToFile, outputFileName):
    global failCount
    # If 'categories.loadTest.tests.api.suite.testName.credentials.required' == true
    if getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['credentials']['required']:
        # If debugMode is neabled
        if debugMode:
          print("["+str(i)+"] Request Authentication: Required")
        # Fetches credential from 'credentials' dict - 'categories.loadTest.tests.api.suite.testName.credentials.name'
        credentialName = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['credentials']['name']
        import lib.credentials
        fetchCredentials = lib.credentials.fetchCredentials(credentialName)
        # Converts returned credential to the header name and value
        authHeaderName = fetchCredentials[0]
        authHeaderValue = fetchCredentials[1]
        # If no auth header name/value is returned fail
        if authHeaderName == "NOT_FOUND" or authHeaderValue == "NOT_FOUND":
            print("["+setColor.FAIL+str(i)+setColor.ENDC +"] ERR: Credential for '" + credentialName + "' not found")
            failCount = failCount + 1
            return
        # If request is a get request
        if requestType == 'get':
            # Generates get request w/ Auth header
            with session.get(url, headers={authHeaderName: authHeaderValue},  timeout=timeoutValue) as response:
                data = response.text
                if response.status_code != 200:
                    print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: "+str(response.status_code) + " | ERR: "+str(data))
                    failCount = failCount + 1
                else:
                    # If debugMode, show pass in logs
                    # This is not enabled by default as you could potentially have thousands of requests
                    if debugMode:
                      print("["+setColor.OKGREEN+str(i)+setColor.ENDC+"] STS: " +str(response.status_code))
                return data
        # If request is a post request
        elif requestType.lower() == 'post':
            # Creates a JSON struct to send data to create resource
            requestDataToJSON = {requestData[0]: requestData[1]}
            # Generates a post response w/ Auth headers and JSON data
            with session.post(url, headers={authHeaderName: authHeaderValue}, data=requestDataToJSON, timeout=timeoutValue) as response:
                data = response.text
                if response.status_code != 200:
                    print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: " +
                          str(response.status_code) + " | ERR: "+str(data))
                    failCount = failCount + 1
                else:
                    # If debugMode, show pass in logs
                    # This is not enabled by default as you could potentially have thousands of requests
                    if debugMode:
                      print("["+setColor.OKGREEN+str(i)+setColor.ENDC +
                            "] STS: " + str(response.status_code) + " - " + requestData[1])
                # If outputToFile (bool) then create file ($PWD/tmp/<file>)
                if outputToFile:
                    with open("./tmp/"+outputFileName, "w") as file:
                        file.write(response.text)
                return data
        # If request is a delete request
        elif requestType.lower() == 'delete':
            url = url + "/" + requestData
            with session.delete(url, headers={authHeaderName: authHeaderValue}, timeout=timeoutValue) as response:
                data = response.text
                if outputToFile:
                    os.remove("./tmp/"+outputFileName)
                if response.status_code != 200:
                    print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: " +
                          str(response.status_code) + " | ERR: "+str(data))
                    failCount = failCount + 1
                else:
                    # If debugMode, show pass in logs
                    # This is not enabled by default as you could potentially have thousands of requests
                    if debugMode:
                      print("["+setColor.OKGREEN+str(i)+setColor.ENDC +
                            "] STS: " + str(response.status_code))
                return data
    # If Auth Header is not set, only 'get' type requests can be made
    # This is strictly for best practice reasons
    else:
        # If request is a get request
        if requestType == 'get':
            with session.get(url, timeout=timeoutValue) as response:
                data = response.text
                if response.status_code != 200:
                    print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: " + str(response.status_code) + " | ERR: "+str(data))
                    failCount = failCount + 1
                else:
                    # If debugMode, show pass in logs
                    # This is not enabled by default as you could potentially have thousands of requests
                    if debugMode:
                      print("["+setColor.OKGREEN+str(i)+setColor.ENDC +"] STS: " + str(response.status_code))
                return data
        # Throws failure if 'post' request is selected without Auth header
        elif requestType == 'post':
            data = "'"+requestType+"' request type not supported without authentication set"
            print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: " +
                  str(response.status_code) + " | ERR: "+str(data))
            failCount = failCount + 1
            return ""
        # Throws failure if 'delete' request is selected without Auth header
        elif requestType == 'delete':
            data = "'"+requestType+"' request type not supported without authentication set"
            print("["+setColor.FAIL+str(i)+setColor.ENDC+"] STS: " +
                  str(response.status_code) + " | ERR: "+str(data))
            failCount = failCount + 1
            return ""

        


# Async function to perform simple load test
# requestCount is spread across maxWorkers
# For example: 
# If you have 100 requestCount and 10 maxWorkers,
# You would have 10 separate executions of 10 requests (100/10)
async def simpleLoadTest():
    testName = 'simpleLoadTest'
    # Ensure failCount is reset (likely redundant)
    global failCount
    failCount = 0
    # Concats (global) url and 'categories.loadTest.tests.api.suite.simpleLoadTest.endpoint'
    url = apiURL + \
        getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['endpoint']
    # Sets request count for the test
    loadCount = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['requestCount']
    # Sets failure threshold for the test
    failureThreshhold = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['failureThreshhold']
    # Sets max worker threads and executes
    with ThreadPoolExecutor(max_workers=getMaxWorkers) as executor:
        # Generates requests based on request count
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    request,
                    *(session, i, testName, url, "get", "", False, "")
                )
                for i in range(loadCount)
            ]
            # Runs the above tasks
            for response in await asyncio.gather(*tasks):
                pass 
    # If failCount is above failure threshhold, fail test
    if failCount > failureThreshhold:
        print("- "+testName+" (" + setColor.FAIL + "FAIL" + setColor.ENDC + ")")
        print("  failures: " + str(failCount))
    # If failCount is not above failure threshhold, pass test
    else:
        print("- "+testName+" (" + setColor.OKGREEN + "PASS" + setColor.ENDC + ")")


# Fancy function for generating requests specifically for the creation load test
# This was the only way to get the request to work in the loop
def requestsForCreationLoadTest(session, i, testName, createURL, deleteURL, accountName):
    if debugMode:
      print("["+str(i)+"] - Create ("+accountName+")")
    request(session, i, testName, createURL, "post", ["name", accountName], True, accountName + ".json")
    if debugMode:
      print("["+str(i)+"] - Delete ("+accountName+")")
    request(session, i, testName, deleteURL, "delete", getAccountID(
        "tmp/"+accountName + ".json"), True, "load-test-" + str(i) + "-" + hash + ".json")

# Async function to perform creation load test
# requestCount is spread across maxWorkers
# For example:
# If you have 100 requestCount and 10 maxWorkers,
# You would have 10 separate executions of 10 requests (100/10)
async def creationLoadTest():
    testName = 'creationLoadTest'
    # Ensure failCount is reset (likely redundant)
    global failCount
    failCount = 0
    # Iterates over 'categories.loadTest.tests.api.suite.creationLoadTest.sets' dict
    for s in range(len(getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'])):
        # Concats (global) url and 'categories.loadTest.tests.api.suite.creationLoadTest.sets.<Index-Value>.create.endpoint'
        createURL = apiURL + getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['create']['endpoint']
        # Concats (global) url and 'categories.loadTest.tests.api.suite.creationLoadTest.sets.<Index-Value>.delete.endpoint'
        deleteURL = apiURL + getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['delete']['endpoint']
        setName = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['name']
        # Checks if 'categories.loadTest.tests.api.suite.creationLoadTest.sets.<Index-Value>.enable' == true
        if getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['enable']:
            # Gets request count for the set
            loadCount = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['requestCount']
            # Sets failure threshold for the set
            failureThreshhold = getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['failureThreshhold']
            if debugMode:
                print("Running test for '" +setName+"'")
            # Sets max worker threads and executes
            with ThreadPoolExecutor(max_workers=getMaxWorkers) as executor:
                # Generates requests based on request count
                with requests.Session() as session:
                    loop = asyncio.get_event_loop()
                    # If 'categories.loadTest.tests.api.suite.creationLoadTest.sets.<Index-Value>.delete.enable' == true
                    if getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['sets'][s]['delete']['enable']:
                        tasks = [
                            loop.run_in_executor(executor, requestsForCreationLoadTest, *(session, i, testName, createURL, deleteURL, "load-test-" + str(i) + "-" + hash))
                            # Loops till request count is met
                            for i in range(loadCount)
                        ]
                    # If 'categories.loadTest.tests.api.suite.creationLoadTest.sets.<Index-Value>.delete.enable' == false
                    else:
                        tasks = [
                            loop.run_in_executor(executor, request,*(session, i, testName, createURL, "post", "load-test-" + str(i) + "-" + hash))
                            for i in range(loadCount)
                        ]
                    # Runs the above tasks
                    for response in await asyncio.gather(*tasks):
                        pass
        else:
            if debugMode:
                print("Skipping "+setName+"' | Reason: disabled")
    # If failCount is above failure threshhold, fail test
    if failCount > failureThreshhold:
        print("- "+testName+"(" + setColor.FAIL + "FAIL" + setColor.ENDC + ")")
        print("  failures: " + str(failCount))
    # If failCount is not above failure threshhold, pass test
    else:
        print("- "+testName+" (" + setColor.OKGREEN + "PASS" + setColor.ENDC + ")")

# Func to run tests
def run_tests():

    # Run simple load test
    testName = "simpleLoadTest"
    if getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['enable']:
      loop = asyncio.get_event_loop()
      future = asyncio.ensure_future(simpleLoadTest())
      loop.run_until_complete(future)
    else:
        print("- "+testName+" (" + setColor.WARNING + "SKIP" + setColor.ENDC + ")")

    # Run creationLoadTest
    testName = "creationLoadTest"
    if getConfig['categories']['loadTest']['tests']['api']['suite'][testName]['enable']:
      loop = asyncio.get_event_loop()
      future = asyncio.ensure_future(creationLoadTest())
      loop.run_until_complete(future)
    else:
        print("- "+testName+" (" + setColor.WARNING + "SKIP" + setColor.ENDC + ")")

    


def main():
    # Sets failCount var to count for failures during tests
    global failCount
    failCount = 0
    # Create '$PWD/tmp'
    createTmpDir()
    # Run tests
    run_tests()
    # Delete '$PWD/tmp'
    deleteTmpDir()
