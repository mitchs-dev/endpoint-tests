import requests
import yaml
import sys
import os
from timeit import default_timer

# Opens 'config.yaml' and reads it
configFile = open('config.yaml')
getConfig = yaml.safe_load(configFile)
# Sets baseURL for tool
baseURL = getConfig['config']['baseUrl']
# Sets debugMode (if enabled)
debugMode = getConfig['config']['debugMode']

# $PWD
pwd = sys.path.append(os.getcwd())


# Runs load testing tests
def loadTesting():
    print("----- LOAD TESTING -----")
    # Static var to determine total test count
    # Should be adjusted as new tests are added
    totalTestCount = 2
    # Static var to determine current test
    # Should be left as is
    testCount = 1
    # Check if load testing is enabled
    if getConfig['categories']['loadTest']['enable']:

        # API Load Testing
        import loadTesting.api
        funcName = loadTesting.api
        print("--> "+funcName.__name__+ " [" + str(testCount) + "/"+str(totalTestCount)+"] --")
        testCount = testCount + 1
        if getConfig['categories']['loadTest']['tests']['api']['enable']:
            funcName.main()
        else:
            print("Skipping "+funcName.__name__+" (disabled)")

        # UI Load Testing
        import loadTesting.ui
        funcName = loadTesting.ui
        print("--> "+funcName.__name__ + " [" + str(testCount)+"/"+str(totalTestCount)+"]")
        testCount = testCount + 1
        if getConfig['categories']['loadTest']['tests']['ui']['enable']:
            print("Run UI Test")
            funcName.main()
        else:
            print("Skipping " + funcName.__name__+" (disabled)")

    else:
        print("Load Testing is disabled")
        print("Skipping...")


if __name__ == "__main__":
    # Checks for 'config.debugMode'
    if debugMode:
        print("Debug Mode enabled")
        print("Max workers: " + str(getConfig['config']['maxWorkers']))
    # Load testing
    loadTesting()
    sys.exit(0)
