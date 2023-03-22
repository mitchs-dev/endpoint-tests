
import yaml

# Opens 'config.yaml' and reads
configFile = open('config.yaml')
getConfig = yaml.safe_load(configFile)
# Sets debug mode (if enabled)
debugMode = getConfig['config']['debugMode']

# Fetches credential from 'credentials' dict
def fetchCredentials(credentialName):
    # Iterates over 'credentials' dict
    for i in range(len(getConfig['credentials'])):
        # Return credential as 'key, value'
        if credentialName == getConfig['credentials'][i]['name']:
            return getConfig['credentials'][i]['key'], getConfig['credentials'][i]['value']
    # If credential not found, return 'NOT_FOUND, NOT_FOUND'
    return "NOT_FOUND", "NOT_FOUND"
